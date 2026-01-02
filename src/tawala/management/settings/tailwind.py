from pathlib import Path

from tawala.management.utils.constants import UI, UI_PATH

from .base import MAIN_INSTALLED_APP
from .conf import Conf, ConfField


class TailwindConf(Conf):
    """Tailwind configuration settings."""

    _default_version = "v4.1.18"

    version = ConfField(
        env="TAILWIND_VERSION",
        toml="tailwind.version",
        default=_default_version,
        type=str,
    )
    cli = ConfField(
        env="TAILWIND_CLI",
        toml="tailwind.cli",
        default=Path(f"~/.local/bin/tailwind-{_default_version}.exe").expanduser(),
        type=Path,
    )
    source = ConfField(
        default=Path.cwd() / MAIN_INSTALLED_APP / "static" / MAIN_INSTALLED_APP / "index.css",
        type=Path,
    )
    output = ConfField(
        default=UI_PATH / "static" / UI / "base" / "index.css",
        type=Path,
    )


TAILWIND = TailwindConf()


__all__ = ["TAILWIND"]
