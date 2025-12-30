from pathlib import Path
from typing import Any, TypedDict

from .. import PROJECT_ROOT


class ProjectConf:
    def __init__(self) -> None:
        self.env = PROJECT_ROOT.env
        self.toml = PROJECT_ROOT.toml
        self.dir: Path = PROJECT_ROOT.dir


class ProjectDirsDict(TypedDict):
    """Type definition for project directories dictionary."""

    BASE: Path
    APP: Path
    API: Path
    PUBLIC: Path


class ProjectDict(TypedDict):
    """Type definition for project configuration dictionary."""

    env: dict[str, str]
    toml: dict[str, Any]
    dirs: ProjectDirsDict


_project = ProjectConf()

PROJECT: ProjectDict = {
    "env": _project.env,
    "toml": _project.toml,
    "dirs": {
        "BASE": _project.dir,
        "APP": _project.dir / "app",
        "API": _project.dir / "api",
        "PUBLIC": _project.dir / "public",
    },
}


__all__ = ["PROJECT"]
