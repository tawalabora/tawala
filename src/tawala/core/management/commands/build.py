"""Management command: build"""

from typing import Any

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandParser


class Command(BaseCommand):
    help = "Execute build commands defined in ENV (BUILD_COMMANDS) or pyproject tool.tawala.build-commands"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show commands that would be executed without running them",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        dry_run: bool = options.get("dry_run", False)
        build_commands: list[str] = getattr(settings, "BUILD_COMMANDS", [])

        if not build_commands:
            self.stdout.write(
                self.style.WARNING(
                    "No build commands configured in settings.BUILD_COMMANDS"
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f"Found {len(build_commands)} build command(s)")
        )

        if dry_run:
            self.stdout.write(self.style.NOTICE("\n=== DRY RUN MODE ==="))
            for i, cmd in enumerate(build_commands, 1):
                self.stdout.write(f"{i}. {cmd}")
            return

        # Execute each build command
        for i, cmd in enumerate(build_commands, 1):
            self.stdout.write(
                self.style.NOTICE(f"\n[{i}/{len(build_commands)}] Running: {cmd}")
            )

            try:
                # Parse command and arguments
                parts: list[str] = cmd.split()
                command_name: str = parts[0]
                command_args: list[str] = parts[1:] if len(parts) > 1 else []

                # Execute the management command
                call_command(command_name, *command_args)

                self.stdout.write(self.style.SUCCESS(f"✓ Completed: {cmd}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ Failed: {cmd}"))
                self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
                # Continue with remaining commands even if one fails
                continue

        self.stdout.write(self.style.SUCCESS("\n=== Build process completed ==="))
