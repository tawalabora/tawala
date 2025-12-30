from typing import TypedDict

from .conf import Conf, ConfField


class SiteConf(Conf):
    """Site-related configuration settings."""

    name = ConfField(env="SITE_NAME", toml="site.name", type=str)
    short_name = ConfField(env="SITE_SHORT_NAME", toml="site.short-name", type=str)
    description = ConfField(env="SITE_DESCRIPTION", toml="site.description", type=str)


class SiteDict(TypedDict):
    name: str
    short_name: str
    description: str


_site = SiteConf()

SITE: SiteDict = {
    "name": _site.name or "Tawala",
    "short_name": _site.short_name or "Tawala",
    "description": _site.description or "Tawala Application",
}

__all__ = ["SITE"]
