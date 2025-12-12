from pathlib import Path
from typing import Type

from christianwhocodes.generators.file import (
    FileGenerator,
    PgPassFileGenerator,
    PgServiceFileGenerator,
    SSHConfigFileGenerator,
)
from django.core.management.base import BaseCommand, CommandError, CommandParser

from .... import BASE_DIR_SETTING


class VercelJSONFileGenerator(FileGenerator):
    """
    Generator for Vercel configuration file (vercel.json).

    Creates a vercel.json file in the Tawala project base directory.
    Useful for deploying Tawala apps to Vercel with custom install/build commands.
    """

    @property
    def file_path(self) -> Path:
        """Return the path for the vercel.json file in BASE_DIR_SETTING."""
        return BASE_DIR_SETTING / "vercel.json"

    @property
    def data(self) -> str:
        """Return template content for vercel.json file."""
        return (
            "{\n"
            '  "$schema": "https://openapi.vercel.sh/vercel.json",\n'
            '  "installCommand": "uv run tawala run -i",\n'
            '  "buildCommand": "uv run tawala run -b",\n'
            '  "rewrites": [\n'
            "    {\n"
            '      "source": "/(.*)",\n'
            '      "destination": "/api/asgi"\n'
            "    }\n"
            "  ]\n"
            "}\n"
        )


class Command(BaseCommand):
    help: str = "Generate configuration files (e.g., vercel.json, .pg_service.conf, pgpass.conf / .pgpass, ssh config)."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "-f",
            "--file",
            choices=["vercel", "pg_service", "pgpass", "ssh_config"],
            type=str,
            required=True,
            help="Specify which file to generate (options: vercel, pg_service, pgpass, ssh_config).",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force overwrite without confirmation.",
        )

    def handle(self, *args, **options) -> None:
        file_option: str = options["file"].lower()
        force: bool = options["force"]

        generators: dict[str, Type[FileGenerator]] = {
            "vercel": VercelJSONFileGenerator,
            "pg_service": PgServiceFileGenerator,
            "pgpass": PgPassFileGenerator,
            "ssh_config": SSHConfigFileGenerator,
        }

        if file_option not in generators:
            raise CommandError(
                f"Unknown file type '{file_option}'. "
                f"Valid options are: {', '.join(generators.keys())}"
            )

        generator_class: Type[FileGenerator] = generators[file_option]
        generator: FileGenerator = generator_class()
        generator.create(force=force)
