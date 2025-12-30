from pathlib import Path
from typing import NotRequired, TypedDict

from .conf import Conf, ConfField
from .project import PROJECT


class DBConf(Conf):
    """Database configuration settings."""

    backend = ConfField(env="DB_BACKEND", toml="db.backend", type=str)
    service = ConfField(env="DB_SERVICE", toml="db.service", type=str)
    pool = ConfField(env="DB_POOL", toml="db.pool", type=bool)
    ssl_mode = ConfField(env="DB_SSL_MODE", toml="db.ssl-mode", type=str)
    use_vars = ConfField(env="DB_USE_VARS", toml="db.use-vars", type=bool)
    user = ConfField(env="DB_USER", type=str)
    password = ConfField(env="DB_PASSWORD", type=str)
    name = ConfField(env="DB_NAME", type=str)
    host = ConfField(env="DB_HOST", type=str)
    port = ConfField(env="DB_PORT", type=str)


class DBOptionsDict(TypedDict, total=False):
    """Type definition for database OPTIONS dictionary."""

    service: str
    pool: bool
    sslmode: str


class DBDict(TypedDict):
    """Type definition for default database configuration."""

    ENGINE: str
    NAME: str | Path
    USER: NotRequired[str | None]
    PASSWORD: NotRequired[str | None]
    HOST: NotRequired[str | None]
    PORT: NotRequired[str | None]
    OPTIONS: NotRequired[DBOptionsDict]


class DatabasesDict(TypedDict):
    """Type definition for DATABASES setting."""

    default: DBDict


_db = DBConf()
# ==============================================================================
# Database Configuration
# https://docs.djangoproject.com/en/stable/ref/databases/#postgresql-notes
# https://www.postgresql.org/docs/current/libpq-pgservice.html
# https://www.postgresql.org/docs/current/libpq-pgpass.html
# ==============================================================================


def _get_databases_config() -> DatabasesDict:
    """Generate databases configuration based on backend type."""

    backend: str = _db.backend.lower() or "sqlite3"

    match backend:
        case "sqlite" | "sqlite3":
            return {
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": PROJECT["dirs"]["BASE"] / "db.sqlite3",
                }
            }
        case "postgresql" | "postgres" | "psql" | "pgsql" | "pg" | "psycopg":
            options: DBOptionsDict = {
                "pool": _db.pool if _db.pool is not None else False,
                "sslmode": _db.ssl_mode or "prefer",
            }

            # Add service or connection vars
            if (_db.use_vars if _db.use_vars is not None else False) is True:
                config: DBDict = {
                    "ENGINE": "django.db.backends.postgresql",
                    "NAME": _db.name,
                    "USER": _db.user,
                    "PASSWORD": _db.password,
                    "HOST": _db.host,
                    "PORT": _db.port,
                    "OPTIONS": options,
                }
            else:
                options["service"] = _db.service
                config = {
                    "ENGINE": "django.db.backends.postgresql",
                    "NAME": _db.name,
                    "OPTIONS": options,
                }

            return {"default": config}
        case _:
            raise ValueError(f"Unsupported DB backend: {backend}")


DATABASES: DatabasesDict = _get_databases_config()
__all__ = ["DATABASES"]
