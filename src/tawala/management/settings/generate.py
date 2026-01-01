from pathlib import Path

from .conf import Conf, ConfField


class FileGeneratorPathsConf(Conf):
    """Generated files configuration settings."""

    _base_dir = Path.cwd()

    env = ConfField(default=_base_dir / ".env.example", type=Path)
    vercel = ConfField(default=_base_dir / "vercel.json", type=Path)
    asgi = ConfField(default=_base_dir / "api" / "asgi.py", type=Path)
    wsgi = ConfField(default=_base_dir / "api" / "wsgi.py", type=Path)


FILE_GENERATOR_PATHS = FileGeneratorPathsConf()


__all__ = ["FILE_GENERATOR_PATHS"]
