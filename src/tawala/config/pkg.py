from pathlib import Path
from typing import TypedDict

from .. import PACKAGE


class PackageConf:
    def __init__(self) -> None:
        self.dir: Path = PACKAGE.dir
        self.name: str = PACKAGE.name
        self.version: str = PACKAGE.version


class PackageDict(TypedDict):
    dir: Path
    name: str
    version: str


_pkg = PackageConf()

PKG: PackageDict = {
    "dir": _pkg.dir,
    "name": _pkg.name,
    "version": _pkg.version,
}

__all__ = ["PKG"]
