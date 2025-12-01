from pathlib import Path
from typing import TypedDict


class ProjectDirsSetting(TypedDict):
    BASE: Path
    APP: Path
    API: Path
    PUBLIC: Path
    CLI: Path
    PACKAGE: Path


class TailwindSetting(TypedDict):
    CLI_PATH: str
    INPUT_CSS: str
    OUTPUT_CSS: str
