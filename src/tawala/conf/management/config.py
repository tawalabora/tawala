import os
import tomllib
from pathlib import Path
from typing import Any, Dict, Optional

from .fields import BaseConfField, ConfField
from .path import BaseDirectory, get_base_dir_or_exit
from .types import KeyType, TomlSectionType, ValueType


class BaseConfig:
    """Base configuration class that handles loading from environment variables and TOML files."""

    _toml_data: Dict[str, ValueType] = {}
    _config_specs = {}

    @classmethod
    def _load_toml(
        cls,
        toml_path: Optional[Path] = None,
        section: TomlSectionType = None,
    ) -> None:
        """Load TOML configuration from pyproject.toml file."""
        if toml_path is None:
            # * Ensure that the validation of base_dir has already occurred
            toml_path = BaseDirectory.get_cached_base_dir() / "pyproject.toml"

        if toml_path.exists():
            with toml_path.open("rb") as f:
                all_data = tomllib.load(f)

            if section:
                data: Any = all_data
                for key in section.split("."):
                    if isinstance(data, dict):
                        data = data.get(key, {})
                    else:
                        data = {}
                        break
                cls._toml_data = data if isinstance(data, dict) else {}
            else:
                cls._toml_data = {}
        else:
            cls._toml_data = {}

    @classmethod
    def _get_from_toml(
        cls,
        key: KeyType,
        section: TomlSectionType = "tool.tawala",
        default: ValueType = None,
    ) -> Any:
        """
        Get value from TOML configuration.

        Args:
            key: Dot-separated path to the config value (e.g., "storage.backend")
            section: The TOML section to load (e.g., "tool.tawala")
            default: Default value if key is not found

        Returns:
            The value from TOML, or the default if not found
        """
        if key is None:
            return default

        # Ensure TOML is loaded with the correct section
        cls._load_toml(section=section)

        # Navigate through nested keys
        current = cls._toml_data
        for k in key.split("."):
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default

        return current

    @classmethod
    def _fetch_value(
        cls,
        env_key: KeyType = None,
        toml_key: KeyType = None,
        default: ValueType = None,
        toml_section: TomlSectionType = "tool.tawala",
    ) -> ValueType:
        """
        Fetch configuration value with fallback priority: ENV -> TOML -> default.

        Args:
            env_key: Environment variable name to check
            toml_key: TOML key path to check (dot-separated)
            default: Default value if neither source has the value
            toml_section: TOML section to search in

        Returns:
            The configuration value from the first available source (raw, no casting)
        """
        # Try environment variable first (if env_key is provided and exists)
        if env_key is not None and env_key in os.environ:
            return os.environ[env_key]

        # Fall back to TOML config and set default as it is the final fallback
        return cls._get_from_toml(toml_key, section=toml_section, default=default)

    def __init_subclass__(cls) -> None:
        """
        Automatically convert ConfField descriptors to properties
        when a subclass is created.
        """
        super().__init_subclass__()
        cls._config_specs = dict(getattr(cls, "_config_specs", {}))

        for attr_name, attr_value in list(vars(cls).items()):
            # Skip private attributes, methods, and special descriptors
            if (
                attr_name.startswith("_")
                or callable(attr_value)
                or isinstance(attr_value, (classmethod, staticmethod, property))
            ):
                continue

            # Check if this is a BaseConfField (ConfField)
            if not isinstance(attr_value, BaseConfField):
                continue

            config_dict = attr_value.to_dict()

            # Store the configuration spec for this field
            cls._config_specs[attr_name] = config_dict

            # Create property getter
            def make_getter(name: str, cfg: Dict[str, Any], field: BaseConfField):
                def getter(self: "BaseConfig") -> Any:
                    env_key = cfg["env"]
                    toml_key = cfg["toml"]
                    default = cfg["default"]
                    raw_value = self._fetch_value(env_key, toml_key, default)

                    # ? What if raw_value is None?

                    # Convert to the appropriate type
                    # ? Will it bring problems here?
                    return field._convert_value(raw_value)

                return getter

            # ?: Can this handle situaltions where the raw_value is None?
            setattr(
                cls,
                attr_name,
                property(make_getter(attr_name, config_dict, attr_value)),
            )

    @classmethod
    def list_env_keys(cls):
        """List all environment variable keys used by this config class."""
        pass


class SecurityConfig(BaseConfig):
    """Security-related configuration settings."""

    secret_key = ConfField(
        env="SECRET_KEY",
        toml="secret-key",
    )
    debug = ConfField(
        env="DEBUG",
        toml="debug",
        default=True,
    )
    allowed_hosts = ConfField(
        env="ALLOWED_HOSTS",
        toml="allowed-hosts",
    )


class ApplicationConfig(BaseConfig):
    """Application and URL configuration settings."""

    configured_apps = ConfField(
        env="CONFIGURED_APPS",
        toml="configured-apps",
    )


class DatabaseConfig(BaseConfig):
    """Database configuration settings."""

    backend = ConfField(
        env="DB_BACKEND",
        toml="db.backend",
        default="sqlite3",
    )
    service = ConfField(
        env="PG_SERVICE",
        toml="db.service",
    )
    pool = ConfField(
        env="DB_POOL",
        toml="db.pool",
        default=False,
    )
    ssl_mode = ConfField(
        env="DB_SSL_MODE",
        toml="db.ssl-mode",
        default="prefer",
    )
    use_vars = ConfField(
        env="DB_USE_VARS",
        toml="db.use-vars",
        default=False,
    )

    user = ConfField(env="DB_USER", default="postgres")
    password = ConfField(env="DB_PASSWORD")
    name = ConfField(env="DB_NAME", default="postgres")
    host = ConfField(env="DB_HOST", default="localhost")
    port = ConfField(env="DB_PORT", default="5432")


class StorageConfig(BaseConfig):
    """Storage configuration settings."""

    backend = ConfField(
        env="STORAGE_BACKEND",
        toml="storage.backend",
        default="filesystem",
    )
    token = ConfField(
        env="STORAGE_TOKEN",
        toml="storage.token",
    )


class BuildConfig(BaseConfig):
    """Build process configuration settings."""

    commands = ConfField(
        env="BUILD_COMMANDS",
        toml="build-commands",
    )


class Tawala:
    """Main configuration class that orchestrates environment, security, app, and database configs."""

    def __init__(self):
        # Check if base_dir has already been validated (e.g., by CLI startup)
        # If not, validate it now (e.g., ASGI/WSGI startup)
        cached_base_dir = BaseDirectory.get_cached_base_dir()

        if cached_base_dir is not None:
            # Already checked by CLI - reuse the cached value
            self.base_dir = cached_base_dir
        else:
            # Not yet checked (ASGI/WSGI context) - check now or exit
            self.base_dir = get_base_dir_or_exit()

        self.security = SecurityConfig()
        self.apps = ApplicationConfig()
        self.db = DatabaseConfig()
        self.storage = StorageConfig()
        self.build = BuildConfig()
