# apps.py

from django.apps import AppConfig

class UserConfig(AppConfig):
    name = 'user'

    def ready(self):
        import user.signals  # Import the signals to ensure they are loaded
