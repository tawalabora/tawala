"""
Initialization configuration.

Exposes `PKG`, `PROJECT`, `DJANGO_SETTINGS_MODULE` for early initialization of:
- cli.py
- settings/conf.py

Import these symbols before Django loads apps and settings; avoid using them elsewhere.
"""

from os import environ
from pathlib import Path
from typing import Any, NoReturn, Optional

from christianwhocodes.helpers import ExitCode, PyProject, Version
from christianwhocodes.stdout import Text, print
from dotenv import dotenv_values


class _Package:
    _file: Path = Path(__file__).resolve()

    def __init__(self) -> None:
        self.dir: Path = self._file.parent
        self.name: str = self.dir.stem
        self.version = Version.get(self.name)[0]


PKG = _Package()

DJANGO_SETTINGS_MODULE = f"{PKG.name}.settings.main"


class _Project:
    """Directory path configuration and validation of project structure."""

    _dir: Optional[Path] = None
    _toml_section: Optional[dict[str, Any]] = None
    _valid_project: Optional[bool] = None

    @classmethod
    def _load_project(cls) -> Optional[NoReturn]:
        try:
            dir: Path = Path.cwd()
            toml_section: dict[str, Any] = PyProject(dir / "pyproject.toml").data["tool"][PKG.name]

        except (FileNotFoundError, KeyError):
            cls._valid_project = False
            print(
                f"Are you currently executing in a {PKG.name.capitalize()} app base directory? "
                f"If not navigate to your app's root or create a new {PKG.name.capitalize()} app to run the command.\n"
                f"'tool.{PKG.name}'section must be included in 'pyproject.toml' even if empty, "
                f"as it serves as a {PKG.name.capitalize()} app project identifier.",
                Text.WARNING,
            )

        except Exception as e:
            cls._valid_project = False
            print(str(e))

        else:
            cls._valid_project = True
            cls._dir = dir
            cls._toml_section = toml_section

        finally:
            if not cls._valid_project:
                from sys import exit

                exit(ExitCode.ERROR)

    @property
    def dir(self) -> Path:
        if not self._valid_project:
            self._load_project()

        assert self._dir is not None
        return self._dir

    @property
    def toml(self) -> dict[str, Any]:
        if not self._valid_project:
            self._load_project()

        assert self._toml_section is not None
        return self._toml_section

    @property
    def env(self) -> dict[str, Any]:
        """Get combined .env and environment variables as a dictionary."""
        return {
            **dotenv_values(self.dir / ".env"),
            **environ,  # override loaded values with environment variables
        }


PROJECT = _Project()


__all__ = ["PKG", "DJANGO_SETTINGS_MODULE", "PROJECT"]
