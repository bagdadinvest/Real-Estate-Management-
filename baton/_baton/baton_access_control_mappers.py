import inspect
from abc import ABCMeta, abstractmethod
from typing import Iterable, Sequence, Union, Dict, Set, List, Any

from baton._baton._baton_runner import BatonRunner, BatonBinary
from baton._baton._constants import BATON_ACL_PROPERTY, BATON_CHMOD_RECURSIVE_FLAG, BATON_LIST_ACCESS_CONTROLS_FLAG
from baton._baton.json import DataObjectJSONEncoder, CollectionJSONEncoder, \
    AccessControlSetJSONDecoder
from baton.mappers import AccessControlMapper, CollectionAccessControlMapper
from baton.models import AccessControl, DataObject, IrodsEntity, Collection, User


class _BatonAccessControlMapper(BatonRunner, AccessControlMapper, metaclass=ABCMeta):
    """
    Access control mapper, implemented using baton.
    """
    _ACCESS_CONTROL_SET_JSON_ENCODER = AccessControlSetJSONDecoder()

    @abstractmethod
    def _create_entity_with_path(self, path: str) -> IrodsEntity:
        """
        Creates an entity model with the given path.
        :param path: the path the entity should have
        :return: the created entity model
        """

    @abstractmethod
    def _entity_to_baton_json(self, entity: IrodsEntity) -> Dict:
        """
        Converts an entity model to its baton JSON representation.
        :param entity: the entity to produce the JSON representation of
        :return: the JSON representation
        """

    def get_all(self, paths: Union[str, Sequence[str]]) -> Union[Set[AccessControl], Sequence[Set[AccessControl]]]:
        single_path = False
        if isinstance(paths, str):
            single_path = True
            paths = [paths]

        baton_in_json = []
        for path in paths:
            baton_in_json.append(self._path_to_baton_json(path))

        baton_out_as_json = self.run_baton_query(
            BatonBinary.BATON_LIST, [BATON_LIST_ACCESS_CONTROLS_FLAG], input_data=baton_in_json)
        assert len(baton_out_as_json) == len(paths)

        access_controls_for_paths = []
        for entity_as_baton_json in baton_out_as_json:
            access_controls_as_baton_json = entity_as_baton_json[BATON_ACL_PROPERTY]
            access_contorls = _BatonAccessControlMapper._ACCESS_CONTROL_SET_JSON_ENCODER.decode_parsed(
                access_controls_as_baton_json)
            access_controls_for_paths.append(access_contorls)

        return access_controls_for_paths[0] if single_path else access_controls_for_paths

    def add_or_replace(self, paths: Union[str, Iterable[str]],
                       access_controls: Union[AccessControl, Iterable[AccessControl]]):
        if isinstance(paths, str):
            paths = [paths]
        if isinstance(access_controls, AccessControl):
            access_controls = [access_controls]

        baton_in_json = []
        for path in paths:
            entity = self._create_entity_with_path(path)
            entity.access_controls = access_controls
            baton_in_json.append(self._entity_to_baton_json(entity))
        self.run_baton_query(BatonBinary.BATON_CHMOD, input_data=baton_in_json)

    def set(self, paths: Union[str, Iterable[str]], access_controls: Union[AccessControl, Iterable[AccessControl]]):
        if isinstance(paths, str):
            paths = [paths]
        if isinstance(access_controls, AccessControl):
            access_controls = [access_controls]

        # baton-chmod does a mix of set and add: adds if no level has been defined for a user, else sets if it has.
        # Taking easiest route of starting from a blank slate
        self.revoke_all(paths)

        baton_in_json = []
        for path in paths:
            entity = self._create_entity_with_path(path)
            entity.access_controls = access_controls
            baton_in_json.append(self._entity_to_baton_json(entity))
        self.run_baton_query(BatonBinary.BATON_CHMOD, input_data=baton_in_json)

    def revoke(self, paths: Union[str, Iterable[str]], users: Union[str, Iterable[str], User, Iterable[User]]):
        if isinstance(paths, str):
            paths = [paths]
        if isinstance(users, str) or isinstance(users, User):
            users = [users]

        for i in range(len(users)):
            if not isinstance(users[i], User):
                assert isinstance(users[i], str)
                user = User.create_from_str(users[i])
                users[i] = user

        no_access_controls = [AccessControl(users, AccessControl.Level.NONE) for users in users]
        self.add_or_replace(paths, no_access_controls)

    def revoke_all(self, paths: Union[str, Iterable[str]]):
        if isinstance(paths, str):
            paths = [paths]

        access_controls_for_paths = self.get_all(paths)

        baton_in_json = []
        for i in range(len(access_controls_for_paths)):
            access_controls = access_controls_for_paths[i]
            path = paths[i]
            for access_control in access_controls:
                access_control.level = AccessControl.Level.NONE
            entity = self._create_entity_with_path(path)
            entity.access_controls = access_controls
            baton_in_json.append(self._entity_to_baton_json(entity))
        self.run_baton_query(BatonBinary.BATON_CHMOD, input_data=baton_in_json)

    def _path_to_baton_json(self, path: str) -> Dict:
        """
        Converts a path to the type of iRODS entity the mapper deals with, to its JSON representation.
        :param path: the path to convert
        :return: the JSON representation of the path
        """
        entity = self._create_entity_with_path(path)
        return self._entity_to_baton_json(entity)


class BatonDataObjectAccessControlMapper(_BatonAccessControlMapper, AccessControlMapper):
    """
    Access control mapper for controls relating specifically to data objects, implemented using baton.
    """
    def _create_entity_with_path(self, path: str) -> DataObject:
        return DataObject(path)

    def _entity_to_baton_json(self, entity: DataObject) -> Dict:
        return DataObjectJSONEncoder().default(entity)


class BatonCollectionAccessControlMapper(_BatonAccessControlMapper, CollectionAccessControlMapper):
    """
    Access control mapper for controls relating specifically to collections, implemented using baton.
    """
    # Note: In hindsight, the hijacking of the recursive chmod request was more complex than initially thought.
    # Complexity is of course never a good thing as it increases the chance that a bug is hiding in here somewhere (for
    # example, will this hijacking still work if the code is compiled?). The alternative to this method would be to
    # modify the superclass and make it accept arguments that it uses when `run_baton_query` is called. Given that the
    # current solution has so far shown itself to work as expected, there is little point changing this until issues
    # are found with it.
    def __init__(self, *args, **kwargs):
        """
        Constructor.
        """
        super().__init__(*args, **kwargs)
        self._original_run_baton_query = self.run_baton_query
        self._hijack_frame_ids = set()    # type: Set[int]
        self.run_baton_query = self._hijacked_run_baton_query

    def set(self, paths: Union[str, Iterable[str]], access_controls: Union[AccessControl, Iterable[AccessControl]],
            recursive: bool=False):
        if recursive:
            self._do_recursive(super().set, paths, access_controls)
        else:
            super().set(paths, access_controls)

    def add_or_replace(self, paths: Union[str, Iterable[str]],
                       access_controls: Union[AccessControl, Iterable[AccessControl]], recursive: bool=False):
        if recursive:
            self._do_recursive(super().add_or_replace, paths, access_controls)
        else:
            super().add_or_replace(paths, access_controls)

    def revoke(self, paths: Union[str, Iterable[str]], users: Union[str, Iterable[str], User, Iterable[User]],
               recursive: bool=False):
        if recursive:
            self._do_recursive(super().revoke, paths, users)
        else:
            super().revoke(paths, users)

    def revoke_all(self, paths: Union[str, Iterable[str]], recursive: bool=False):
        if recursive:
            self._do_recursive(super().revoke_all, paths)
        else:
            super().revoke_all(paths)

    def _create_entity_with_path(self, path: str) -> DataObject:
        return Collection(path)

    def _entity_to_baton_json(self, entity: Collection) -> Dict:
        return CollectionJSONEncoder().default(entity)

    def _do_recursive(self, method_that_runs_baton_chmod: callable, *args, **kwargs):
        """
        Adds the `--recursive` argument to all calls to `baton-chmod`.
        :param method_that_runs_baton_chmod: the method that, at a lower level, calls out to baton-chmod
        :param args: positional arguments to call given method with
        :param kwargs: named arguments to call given method with
        """
        current_frame_id = id(inspect.currentframe())
        try:
            self._hijack_frame_ids.add(current_frame_id)
            method_that_runs_baton_chmod(*args, **kwargs)
        finally:
            self._hijack_frame_ids.remove(current_frame_id)

    def _hijacked_run_baton_query(
            self, baton_binary: BatonBinary, program_arguments: List[str]=None, input_data: Any=None) -> List[Dict]:
        """
        Hijacked `run_baton_query` method with hijacking to add the `--recursive` flag to calls to `baton-chmod` that
        originate from code called from frames with the ids in `self._hijack_frame_ids`.
        :param baton_binary: see `BatonRunner.run_baton_query`
        :param program_arguments: see `BatonRunner.run_baton_query`
        :param input_data: see `BatonRunner.run_baton_query`
        :return: see `BatonRunner.run_baton_query`
        """
        if baton_binary == BatonBinary.BATON_CHMOD:
            current_frame = inspect.currentframe()

            def frame_code_in_same_file(frame) -> bool:
                return frame_back.f_code.co_filename == current_frame.f_code.co_filename

            frame_back = current_frame.f_back
            assert frame_code_in_same_file(frame_back)

            while frame_back is not None and frame_code_in_same_file(frame_back):
                if id(frame_back) in self._hijack_frame_ids:
                    return self._original_run_baton_query(baton_binary, [BATON_CHMOD_RECURSIVE_FLAG], input_data)
                frame_back = frame_back.f_back

        return self._original_run_baton_query(baton_binary, program_arguments, input_data)
