from typing import TypedDict

from .conf import Conf, ConfField
from .pkg import PKG


class OrgConf(Conf):
    """Organization-related configuration settings."""

    name = ConfField(env="ORG_NAME", toml="org.name", type=str)
    short_name = ConfField(env="ORG_SHORT_NAME", toml="org.short-name", type=str)
    description = ConfField(env="ORG_DESCRIPTION", toml="org.description", type=str)


class OrgDict(TypedDict):
    name: str
    short_name: str
    description: str


_org = OrgConf()

ORG: OrgDict = {
    "name": _org.name or PKG["name"].capitalize(),
    "short_name": _org.short_name or PKG["name"].capitalize(),
    "description": _org.description or f"{PKG['name'].capitalize()} Application",
}

__all__ = ["ORG"]
