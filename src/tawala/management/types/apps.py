from pathlib import Path
from typing import TypeAlias, TypedDict


class TemplateOptionsDict(TypedDict):
    """Template configuration options."""

    context_processors: list[str]


class TemplateDict(TypedDict):
    """Django template configuration."""

    BACKEND: str
    DIRS: list[Path]
    APP_DIRS: bool
    OPTIONS: TemplateOptionsDict


TemplatesDict: TypeAlias = list[TemplateDict]


__all__ = ["TemplateOptionsDict", "TemplateDict", "TemplatesDict"]
