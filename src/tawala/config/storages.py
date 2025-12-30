from typing import NotRequired, TypedDict
from pathlib import Path

from .conf import Conf, ConfField
from .pkg import PKG
from .project import PROJECT


class StorageConf(Conf):
    """Storage configuration settings."""

    backend = ConfField(env="STORAGE_BACKEND", toml="storage.backend", type=str)
    token = ConfField(env="BLOB_READ_WRITE_TOKEN", toml="storage.token", type=str)


_storage = StorageConf()


class StorageBackendDict(TypedDict, total=False):
    """Type definition for individual storage backend configuration."""

    BACKEND: str
    TOKEN: NotRequired[str | None]


class StoragesDict(TypedDict):
    """Type definition for STORAGES setting."""

    staticfiles: StorageBackendDict
    default: StorageBackendDict


# ==============================================================================
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/stable/howto/static-files/
# ==============================================================================

STATIC_URL: str = "/static/"
STATIC_ROOT: Path = PROJECT["dirs"]["PUBLIC"] / "static"

# ==============================================================================
# Storage & Media files (User-uploaded content)
# https://docs.djangoproject.com/en/stable/ref/settings/#storages
# https://docs.djangoproject.com/en/stable/ref/settings/#media-files
# ==============================================================================


def _get_storages_config() -> StoragesDict:
    """Generate storage configuration based on backend type."""

    backend: str = _storage.backend or "filesystem"

    storage_backend: str
    match backend:
        case "filesystem" | "local" | "fs":
            storage_backend = "django.core.files.storage.FileSystemStorage"
            global MEDIA_URL, MEDIA_ROOT
            MEDIA_URL = "/media/"
            MEDIA_ROOT = PROJECT["dirs"]["PUBLIC"] / "media"

        case "vercel" | "vercelblob" | "vercel_blob" | "vercel-blob":
            storage_backend = f"{PKG['name']}.backends.storage.VercelBlobStorage"

        case _:
            raise ValueError(f"Unsupported storage backend: {backend}")

    return {
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
        "default": {
            "BACKEND": storage_backend,
            "TOKEN": _storage.token,
        },
    }


STORAGES: StoragesDict = _get_storages_config()
__all__ = ["STORAGES", "MEDIA_ROOT", "MEDIA_URL", "STATIC_URL", "STATIC_ROOT"]
