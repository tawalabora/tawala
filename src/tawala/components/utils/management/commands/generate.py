from enum import StrEnum
from pathlib import Path
from typing import Type

from christianwhocodes.generators.file import (
    FileGenerator,
    FileGeneratorOption,
    PgPassFileGenerator,
    PgServiceFileGenerator,
    SSHConfigFileGenerator,
)
from django.core.management.base import BaseCommand, CommandParser

from .... import BASE_DIR_SETTING


class FileOption(StrEnum):
    PG_SERVICE = FileGeneratorOption.PG_SERVICE.value
    PGPASS = FileGeneratorOption.PGPASS.value
    SSH_CONFIG = FileGeneratorOption.SSH_CONFIG.value
    VERCEL = "vercel"


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
            choices=[opt.value for opt in FileOption],
            type=FileOption,
            required=True,
            help=f"Specify which file to generate (options: {', '.join(o.value for o in FileOption)}).",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force overwrite without confirmation.",
        )

    def handle(self, *args, **options) -> None:
        file_option: FileOption = FileOption(options["file"])
        force: bool = options["force"]

        generators: dict[FileOption, Type[FileGenerator]] = {
            FileOption.VERCEL: VercelJSONFileGenerator,
            FileOption.PG_SERVICE: PgServiceFileGenerator,
            FileOption.PGPASS: PgPassFileGenerator,
            FileOption.SSH_CONFIG: SSHConfigFileGenerator,
        }

        generator_class: Type[FileGenerator] = generators[file_option]
        generator: FileGenerator = generator_class()
        generator.create(force=force)
