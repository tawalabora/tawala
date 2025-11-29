from pathlib import Path
from typing import Optional


class NotBaseDirectoryError(Exception):
    """Raised when the current directory is not a Tawala app base directory."""

    pass


class BaseDirectory:
    """Directory path configuration and validation of Tawala app project structure."""

    _cached_base_dir: Optional[Path] = None
    _cached_is_valid: Optional[bool] = None

    @classmethod
    def _detect_base_dir(cls) -> tuple[Path, bool]:
        """Detect if we're in a valid Tawala project and cache the results."""
        cwd = Path.cwd()
        apps_py = cwd / "app" / "apps.py"

        if apps_py.exists():
            return (apps_py.parent.parent, True) if apps_py.is_file() else (cwd, False)
        else:
            return cwd, False

    @classmethod
    def get_base_dir(cls) -> Path:
        """
        Get the Tawala app base directory or raise NotBaseDirectoryError.

        Returns:
            Path: The base directory of the Tawala app.

        Raises:
            NotBaseDirectoryError: If not in a valid Tawala app base directory.
        """
        if cls._cached_base_dir is None:
            cls._cached_base_dir, cls._cached_is_valid = cls._detect_base_dir()

        if not cls._cached_is_valid:
            raise NotBaseDirectoryError(
                "Not a Tawala app base directory. Navigate to your app's root or initialize a new Tawala app."
            )

        return cls._cached_base_dir

    @classmethod
    def get_cached_base_dir(cls) -> Optional[Path]:
        """
        Get the base directory if it has already been validated, otherwise return None.

        This is useful for contexts where validation has already happened
        and we want to reuse the cached result without re-checking.

        Returns:
            Optional[Path]: The cached base directory if already validated, None otherwise.
        """
        if cls._cached_base_dir is not None and cls._cached_is_valid:
            return cls._cached_base_dir
        return None


def get_base_dir_or_exit() -> Path:
    """Get the Tawala app base directory or exit with an error."""
    try:
        return BaseDirectory.get_base_dir()
    except NotBaseDirectoryError as e:
        import sys

        from django.core.management.color import color_style

        print(color_style().ERROR(e))
        sys.exit(1)
