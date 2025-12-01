"""Management command: generate

Generates various project configuration files and secrets. Supports multiple
generators including random secret keys, Vercel configuration files, and
environment configuration files.

Example:
    tawala generate random
    tawala generate random --no-clipboard
    tawala generate vercel
    tawala generate vercel --force
    tawala generate env
    tawala generate env --path /custom/path/.env --force --uncomment
"""

from typing import Any, cast

from django.core.management.base import BaseCommand, CommandParser

from ..generators import EnvGenerator, Generator, RandomGenerator, VercelGenerator


class Command(BaseCommand):
    """Tawala management command for generating project configuration files and secrets.

    This command provides multiple generators for setting up project files:
    - random: Generate a random string suitable for Tawala SECRET_KEY
    - vercel: Generate Vercel configuration (vercel.json)
    - env: Generate environment configuration file (.env)

    Examples:
        # Generate a random secret key with clipboard copy
        tawala generate random

        # Generate without copying to clipboard
        tawala generate random --no-clipboard

        # Generate Vercel configuration
        tawala generate vercel

        # Generate Vercel configuration, overwriting if it exists
        tawala generate vercel --force

        # Generate .env file
        tawala generate env

        # Generate .env file with custom path and options
        tawala generate env --path /custom/path/.env --force --uncomment

        # Use from other management commands
        from django.core.management import call_command
        call_command('generate', 'random')
        call_command('generate', 'vercel', force=True)
        call_command('generate', 'env', uncomment=True)
    """

    help = "Generate various project configuration files and secrets."
    requires_system_checks: bool = cast(bool, [])

    GENERATORS: dict[str, type[Generator]] = {
        "random": RandomGenerator,
        "vercel": VercelGenerator,
        "env": EnvGenerator,
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
            help="Specify what to generate (random, vercel, env)",
        )

        # Random generator option
        parser.add_argument(
            "--no-clipboard",
            action="store_true",
            help="Skip copying the generated string to clipboard (only for 'random' generator)",
        )

        # Vercel and env generator option
        parser.add_argument(
            "-f",
            "--force",
            "--overwrite",
            dest="force",
            action="store_true",
            help="Overwrite existing files without prompting (for 'vercel' and 'env' generators)",
        )

        # Env generator specific options
        parser.add_argument(
            "-p",
            "--path",
            dest="path",
            type=str,
            default=None,
            help="Custom path for the .env file (only for 'env' generator, default: BASE_DIR/.env)",
        )
        parser.add_argument(
            "--uncomment",
            action="store_true",
            help="Leave variables uncommented (active by default) in .env file (only for 'env' generator)",
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
                - force (bool): For 'vercel' and 'env' generators.
                - path (str): For 'env' generator only.
                - uncomment (bool): For 'env' generator only.
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

        # Validate --path is only used with env generator
        if options.get("path") is not None and generator_name != "env":
            self.stdout.write(
                self.style.ERROR(
                    f"--path is only valid for the 'env' generator, not '{generator_name}'"
                )
            )
            return

        # Validate --uncomment is only used with env generator
        if options.get("uncomment", False) and generator_name != "env":
            self.stdout.write(
                self.style.ERROR(
                    f"--uncomment is only valid for the 'env' generator, not '{generator_name}'"
                )
            )
            return

        generator_class = self.GENERATORS[generator_name]
        generator: Generator = generator_class(self)
        generator.handle(*args, **options)
