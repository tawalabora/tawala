from django.apps import AppConfig

from ..core.conf.pre import PKG


class UtilsConfig(AppConfig):
    name = f"{PKG.name}.utils"

    def ready(self):
        # Remove runserver command
        from django.core.management import get_commands

        commands = get_commands()
        if "runserver" in commands:
            commands.pop("runserver")
