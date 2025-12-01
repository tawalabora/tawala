"""Management command: generate

Generates various project configuration files and secrets. Supports multiple
generators including random secret keys and Vercel configuration files.

Example:
    tawala generate random
    tawala generate random --no-clipboard
    tawala generate vercel
    tawala generate vercel --force
"""

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, List, TypedDict, cast

from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser
from django.core.management.utils import get_random_secret_key


class RewriteRule(TypedDict):
    """TypedDict for URL rewrite rules in Vercel configuration.

    Attributes:
        source: The source URL pattern.
        destination: The destination URL pattern.
    """

    source: str
    destination: str


VercelConfig = TypedDict(
    "VercelConfig",
    {
        "$schema": str,
        "buildCommand": str,
        "rewrites": List[RewriteRule],
    },
)


class Generator(ABC):
    """Base class for generators.

    Defines the interface for all generator types. Subclasses must implement
    the handle method to define their specific generation logic.

    Attributes:
        command: Reference to the parent Command instance for output and styling.
    """

    def __init__(self, command: "Command") -> None:
        """Initialize the generator with a command reference.

        Args:
            command: The parent Command instance.
        """
        self.command = command

    @abstractmethod
    def handle(self, *args: Any, **options: Any) -> None:
        """Execute the generator logic.

        Args:
            *args: Positional arguments passed from the command.
            **options: Keyword arguments passed from the command, containing
                parsed command-line options.
        """
        pass


class RandomGenerator(Generator):
    """Generator for random strings suitable for Tawala SECRET_KEY.

    Generates a cryptographically secure random string and optionally copies
    it to the system clipboard using pyperclip.

    Example:
        generator = RandomGenerator(command)
        generator.handle(no_clipboard=False)
    """

    def handle(self, *args: Any, **options: Any) -> None:
        """Generate and display a random string.

        Args:
            *args: Unused positional arguments.
            **options: Command options including:
                - no_clipboard (bool): If True, skip copying to clipboard.
        """
        random_str: str = get_random_secret_key()
        self.command.stdout.write(
            "Generated random string: " + self.command.style.SUCCESS(random_str)
        )

        if not options.get("no_clipboard", False):
            self._copy_to_clipboard(random_str)

    def _copy_to_clipboard(self, text: str) -> None:
        """Copy text to clipboard with error handling.

        Attempts to copy the given text to the system clipboard using pyperclip.
        Gracefully handles the case where pyperclip is not installed or copy fails.

        Args:
            text: The text to copy to the clipboard.
        """
        try:
            import pyperclip

            pyperclip.copy(text)
            self.command.stdout.write(
                self.command.style.SUCCESS("Copied to clipboard successfully.")
            )
        except ImportError:
            self.command.stdout.write(
                self.command.style.ERROR(
                    "pyperclip is not installed. Install it to enable clipboard functionality (uv add pyperclip)."
                )
            )
        except Exception as e:
            self.command.stdout.write(
                self.command.style.WARNING(f"Could not copy to clipboard: {e}")
            )


class VercelGenerator(Generator):
    """Generator for Vercel configuration file.

    Creates a vercel.json configuration file at the project BASE_DIR with
    appropriate build commands and URL rewrites for the ASGI application.
    Prompts for confirmation if the file already exists, unless --force is used.

    Example:
        generator = VercelGenerator(command)
        generator.handle(force=False)

        # With force flag to overwrite without prompting
        generator.handle(force=True)
    """

    def handle(self, *args: Any, **options: Any) -> None:
        """Generate or overwrite the Vercel configuration file.

        Args:
            *args: Unused positional arguments.
            **options: Command options including:
                - force (bool): If True, overwrite existing files without prompting.
        """
        base_dir: Path = Path(settings.BASE_DIR)
        vercel_path: Path = base_dir / "vercel.json"

        # Check if file exists and handle accordingly
        if vercel_path.exists() and not options.get("force", False):
            if not self._prompt_overwrite(vercel_path):
                self.command.stdout.write(
                    self.command.style.WARNING(
                        "Aborted. vercel.json was not overwritten."
                    )
                )
                return

        content: VercelConfig = {
            "$schema": "https://openapi.vercel.sh/vercel.json",
            "buildCommand": "export UV_LINK_MODE=copy; uv run tawala build",
            "rewrites": [{"source": "/(.*)", "destination": "/api/asgi"}],
        }

        try:
            json_text: str = json.dumps(content, indent=2)
            vercel_path.write_text(json_text, encoding="utf-8")

            self.command.stdout.write(
                self.command.style.SUCCESS(f"vercel.json created at: {vercel_path}")
            )
        except Exception as exc:
            self.command.stdout.write(
                self.command.style.ERROR(f"Failed to create vercel.json: {exc}")
            )

    def _prompt_overwrite(self, file_path: Path) -> bool:
        """Prompt user for confirmation to overwrite existing file.

        Args:
            file_path: The path to the existing file.

        Returns:
            True if the user enters 'y' or 'Y', False otherwise (defaults to no).
        """
        prompt: str = (
            f"\n{self.command.style.WARNING(str(file_path))} already exists. "
            f"Overwrite? [y/N]: "
        )
        response: str = input(prompt).strip().lower()
        return response == "y"


class Command(BaseCommand):
    """Tawala management command for generating project configuration files and secrets.

    This command provides multiple generators for setting up project files:
    - random: Generate a random string suitable for Tawala SECRET_KEY
    - vercel: Generate Vercel configuration (vercel.json)

    Examples:
        # Generate a random secret key with clipboard copy
        tawala generate random

        # Generate without copying to clipboard
        tawala generate random --no-clipboard

        # Generate Vercel configuration
        tawala generate vercel

        # Generate Vercel configuration, overwriting if it exists
        tawala generate vercel --force

        # Use from other management commands
        from django.core.management import call_command
        call_command('generate', 'random')
        call_command('generate', 'vercel', force=True)
    """

    help = "Generate various project configuration files and secrets."
    requires_system_checks: bool = cast(bool, [])

    GENERATORS: dict[str, type[Generator]] = {
        "random": RandomGenerator,
        "vercel": VercelGenerator,
    }

    def add_arguments(self, parser: CommandParser) -> None:
        """Define command-line arguments.

        Args:
            parser: The argument parser to add arguments to.
        """
        parser.add_argument(
            "generator",
            type=str,
            choices=self.GENERATORS.keys(),
            help="Specify what to generate (random, vercel)",
        )

        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "--no-clipboard",
            action="store_true",
            help="Skip copying the generated string to clipboard (only for 'random' generator)",
        )
        group.add_argument(
            "-f",
            "--force",
            "--overwrite",
            dest="force",
            action="store_true",
            help="Overwrite existing files without prompting (only for 'vercel' generator)",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Handle the command execution.

        Dispatches to the appropriate generator based on the 'generator' argument.
        Validates that generator-specific flags are used only with their intended generator.

        Args:
            *args: Unused positional arguments.
            **options: Command options including:
                - generator (str): The name of the generator to use.
                - no_clipboard (bool): For 'random' generator only.
                - force (bool): For 'vercel' generator only.
        """
        generator_name: str = options["generator"]

        # Validate --no-clipboard is only used with random generator
        if options.get("no_clipboard", False) and generator_name != "random":
            self.stdout.write(
                self.style.ERROR(
                    f"--no-clipboard is only valid for the 'random' generator, not '{generator_name}'"
                )
            )
            return

        # Validate --force is only used with vercel generator
        if options.get("force", False) and generator_name != "vercel":
            self.stdout.write(
                self.style.ERROR(
                    f"-f / --force / --overwrite is only valid for the 'vercel' generator, not '{generator_name}'"
                )
            )
            return

        generator_class = self.GENERATORS[generator_name]
        generator: Generator = generator_class(self)
        generator.handle(*args, **options)
