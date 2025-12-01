from django.apps import AppConfig


class TawalaUtilsConfig(AppConfig):
    name = "tawala.utils"

    def ready(self):
        # Remove runserver command
        from django.core.management import get_commands

        commands = get_commands()
        if "runserver" in commands:
            commands.pop("runserver")
