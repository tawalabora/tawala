from pathlib import Path
from typing import TypedDict

from .conf import Conf, ConfField
from .pkg import PKG
from .project import PROJECT


class TailwindCSSConf(Conf):
    """TailwindCSS configuration settings."""

    version = ConfField(env="TAILWINDCSS_VERSION", toml="tailwindcss.version", type=str)
    cli = ConfField(env="TAILWINDCSS_CLI", toml="tailwindcss.cli", type=Path)


class TailwindCSSDict(TypedDict):
    """Type definition for TailwindCSS configuration dictionary."""

    version: str
    cli: Path
    source: Path
    output: Path


_tailwindcss = TailwindCSSConf()


def _get_tailwindcss_config() -> TailwindCSSDict:
    """Generate TailwindCSS configuration."""

    version: str = _tailwindcss.version or "v4.1.18"
    cli_path: Path = _tailwindcss.cli or Path(f"~/.local/bin/tailwindcss-{version}.exe").expanduser()

    return {
        "version": version,
        "cli": cli_path,
        "source": PROJECT["dirs"]["APP"] / "static" / "app" / "css" / "source.css",
        "output": PKG["dir"] / "static" / "vendors" / "tailwindcss" / "output.css",
    }


TAILWINDCSS: TailwindCSSDict = _get_tailwindcss_config()
__all__ = ["TAILWINDCSS"]
