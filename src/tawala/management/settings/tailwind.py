from pathlib import Path

from .apps import MAIN_INSTALLED_APP
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
        default=Path.cwd() / MAIN_INSTALLED_APP / "static" / MAIN_INSTALLED_APP / "global.css",
        type=Path,
    )
    output = ConfField(
        default=Path(__file__).resolve().parent.parent.parent
        / "core"
        / "static"
        / "core"
        / "global.css",
        type=Path,
    )


TAILWIND = TailwindConf()


__all__ = ["TAILWIND"]
