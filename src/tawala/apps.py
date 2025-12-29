from django.apps import AppConfig as BaseAppConfig
from . import PKG


class AppConfig(BaseAppConfig):
    name = PKG.name

    # def ready(self):
    #     # Remove runserver command
    #     from django.core.management import get_commands

    #     commands = get_commands()
    #     if "runserver" in commands:
    #         commands.pop("runserver")
