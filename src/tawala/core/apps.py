from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "tawala.core"

    def ready(self):
        # Remove runserver command
        from django.core.management import get_commands

        commands = get_commands()
        if "runserver" in commands:
            commands.pop("runserver")
