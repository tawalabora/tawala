from pathlib import Path
from typing import Literal, NotRequired, TypeAlias, TypedDict

OrgKey: TypeAlias = Literal[
    "name",
    "short-name",
    "description",
    "logo-url",
    "favicon-url",
    "apple-touch-icon-url",
]


class TemplateOptionsDict(TypedDict):
    """Template configuration options."""

    context_processors: list[str]
    builtins: NotRequired[list[str]]
    libraries: NotRequired[dict[str, str]]


class TemplateDict(TypedDict):
    """Django template configuration."""

    BACKEND: str
    DIRS: list[Path]
    APP_DIRS: bool
    OPTIONS: TemplateOptionsDict


TemplatesDict: TypeAlias = list[TemplateDict]


__all__ = ["OrgKey", "TemplateOptionsDict", "TemplateDict", "TemplatesDict"]
