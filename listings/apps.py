from django.apps import AppConfig


class ListingsConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'listings'

    def ready(self):
        # Import signal handlers
        from . import signals  # noqa: F401
