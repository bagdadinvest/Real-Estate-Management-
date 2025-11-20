import collections
from typing import Dict, Sequence, Union, Optional, Sized, Iterable, Any, Set, Container

from hgicommon.collections import Metadata


class IrodsMetadata(Metadata):
    """
    iRODS metadata is in the form of "AVUs" (attribute-value-unit tuples). Attributes may have many values therefore all
    attributes are sets. Units are not currently considered.

    The difference between `Metadata` and `IrodsMetadata` is that the latter ensures that keys are associated to sets of
    values, reflecting what is allowed in iRODS. The methods are subsequently more restrictive than that of the
    superclass, which allows keys to be associated to any value. The current implementation is essentially
    `Dict[str, Set[Any]]` (with convenience methods).
    """
    @staticmethod
    def from_metadata(metadata: Metadata) -> Any:
        """
        Static factory method to create an equivalent instance of this type from the given `Metadata` instance.
        :param metadata: the `Metadata` instance to create an instance of this class from
        :return: the created instance of this class
        """
        irods_metadata = IrodsMetadata()
        for key, value in metadata.items():
            irods_metadata[key] = {value}
        return irods_metadata

    def __init__(self, seq: Dict[Any, Set[str]]=None):
        super().__init__()
        if seq is not None:
            for key, value in seq.items():
                self[key] = value

    def get(self, key: str, default=None) -> Set[str]:
        value = super().get(key, default)
        if value != default:
            assert isinstance(value, collections.Set)
        return value

    def add(self, key: str, value: str):
        """
        Adds the given value to the set of data stored under the given key.
        :param key: the set's key
        :param value: the value to add in the set associated to the given key
        """
        if key in self:
            # Use super to get mutable set
            super().__getitem__(key).add(value)
        else:
            self[key] = {value}

    def __getitem__(self, key: str) -> Set[str]:
        value = super().__getitem__(key)
        assert isinstance(value, collections.Set)
        return value

    def __setitem__(self, key: str, value: Set[str]):
        assert isinstance(value, collections.Set)
        super().__setitem__(key, value)


from baton.models import DataObjectReplica


class DataObjectReplicaCollection(Sized, Iterable, Container):
    """
    Collection of data object replicas.
    """
    def __init__(self, data_object_replicas: Iterable[DataObjectReplica]=()):
        """
        Constructor.
        :param data_object_replicas: (optional) replica to go into this collection initially
        """
        self._data = dict()     # type: Dict[int, DataObjectReplica]
        for data_object_replica in data_object_replicas:
            self.add(data_object_replica)

    def get_by_number(self, number: int) -> Optional[DataObjectReplica]:
        """
        Gets the data object replica in this collection with the given number. Will return `None` if such replica does
        not exist.
        :param number: the number of the data object replica to get
        :return: the data object replica in this collection with the given number
        """
        return self._data.get(number, None)

    def get_out_of_date(self) -> Sequence[DataObjectReplica]:
        """
        Gets any data object replica that are marked as out of date/not in date.
        :return: the out of data object replica
        """
        out_of_date = []
        for number, data_object_replica in self._data.items():
            if not data_object_replica.up_to_date:
                out_of_date.append(data_object_replica)
        return out_of_date

    def add(self, data_object_replica: DataObjectReplica):
        """
        Adds the given data object replica to this collection. Will raise a `ValueError` if a data object replica with
        the same number already exists.
        :param data_object_replica: the data object replica to add
        """
        if data_object_replica.number in self._data:
            raise ValueError(
                    "Data object replica with number %d already exists in this collection" % data_object_replica.number)
        self._data[data_object_replica.number] = data_object_replica

    def remove(self, identifier: Union[DataObjectReplica, int]):
        """
        Removes a data object from this collection that has the given unique identifier. A `ValueError` will be raised
        if a data object with the given identifier does not exist.
        :param identifier: the identifier of the data object
        """
        if isinstance(identifier, int):
            self._remove_by_number(identifier)
        elif isinstance(identifier, DataObjectReplica):
            self._remove_by_object(identifier)
        else:
            raise TypeError("Can only remove by number or by object reference: `%s` given" % type(identifier))

    def _remove_by_number(self, number: int):
        """
        Removes the data object from this collection with the given number. A `ValueError` will be raised if a data
        object with the given number does not exist.
        :param number: the number of the data object to remove
        """
        if number not in self._data:
            raise ValueError("Data object replica number %d is not in this collection" % number)
        del self._data[number]
        assert number not in self._data

    def _remove_by_object(self, data_object_replica: DataObjectReplica):
        """
        Removes the given data object from this collection. A `ValueError` will be raised if the given data object does
        not exist within this collection.
        :param data_object_replica: the data object replica to remove
        """
        self.remove(data_object_replica.number)

    def __eq__(self, other: Any) -> bool:
        if type(other) != DataObjectReplicaCollection:
            return False
        return other._data == self._data

    def __str__(self):
        return str(self._data)

    def __repr__(self):
        return "<%s object at %s: %s>" % (type(self), id(self), str(self))

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterable[DataObjectReplica]:
        return self._data.values().__iter__()

    def __contains__(self, item: Any) -> bool:
        return item in self._data.values()
