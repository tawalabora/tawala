import os
from pathlib import Path
from typing import Any, Dict, NoReturn, Optional

from ..utils.helpers import to_bool, to_list_of_str


class NotBaseDirectoryError(Exception):
    """Raised when the current directory is not a Tawala app base directory."""

    pass


class Project:
    """Directory path configuration and validation of Tawala app project structure."""

    tawala_package_dir = Path(__file__).resolve().parent.parent
    _cached_base_dir: Optional[Path] = None
    _cached_is_valid: Optional[bool] = None
    _cached_toml_section: Optional[dict[str, Any]] = None

    @classmethod
    def _detect_base_dir(cls) -> tuple[Path, bool, Optional[dict[str, Any]]]:
        """Detect if we're in a valid Tawala project and cache the results."""

        cwd = Path.cwd()
        pyproject_toml = cwd / "pyproject.toml"

        if pyproject_toml.exists() and pyproject_toml.is_file():
            import tomllib

            with pyproject_toml.open("rb") as f:
                toml_data = tomllib.load(f)

                # check for [tool.tawala] section
                toml_section: Optional[dict[str, Any]] = toml_data.get("tool", {}).get(
                    "tawala", None
                )
                if toml_section is not None:
                    return pyproject_toml.parent, True, toml_section
                else:
                    return cwd, False, None
        else:
            return cwd, False, None

    @classmethod
    def _get_base_dir_on_initial_load(cls) -> Path:
        """
        Get the Tawala app base directory or raise NotBaseDirectoryError.

        Returns:
            Path: The base directory of the Tawala app.

        Raises:
            NotBaseDirectoryError: If not in a valid Tawala app base directory.
        """
        if cls._cached_base_dir is None:
            cls._cached_base_dir, cls._cached_is_valid, cls._cached_toml_section = (
                cls._detect_base_dir()
            )

        if not cls._cached_is_valid:
            raise NotBaseDirectoryError(
                "Are you currently executing in a Tawala app base directory? "
                "If not navigate to your app's root or "
                "create a new Tawala app to run the command."
            )

        return cls._cached_base_dir

    @classmethod
    def get_base_dir_or_exit(cls) -> Path | NoReturn:
        """Get the Tawala app base directory or exit with an error."""
        try:
            return cls._get_base_dir_on_initial_load()
        except NotBaseDirectoryError as e:
            import sys

            from django.core.management.color import color_style

            print(color_style().WARNING(str(e)))
            sys.exit(1)

    @classmethod
    def get_base_dir(cls) -> Path:
        """
        * Only use when the base directory has already been validated.

        Returns:
            Path: The base directory.
        """
        if cls._cached_is_valid and cls._cached_base_dir is not None:
            return cls._cached_base_dir
        else:
            return cls.get_base_dir_or_exit()

    @classmethod
    def get_toml_section(cls) -> dict[str, Any]:
        """
        * Only use when the pyproject.toml [tool.tawala] section has already been validated.

        Returns:
            dict[str, Any]: The [tool.tawala] section in pyproject.toml.
        """
        assert cls._cached_toml_section is not None, (
            "Only use when the pyproject.toml [tool.tawala] section has already been validated."
        )
        return cls._cached_toml_section


class ConfField:
    """
    Configuration field descriptor.

    This class defines a configuration field that can be populated from either
    environment variables or TOML configuration files, with a fallback default value.

    Args:
        env: Environment variable name to read from
        toml: TOML key path (dot-separated) to read from
        default: Default value if neither source provides a value
    """

    # Define which fields need special type handling
    BOOL_FIELDS = {"debug", "pool", "use_vars"}
    LIST_FIELDS = {"allowed_hosts", "configured_apps", "commands"}

    def __init__(
        self,
        env: Optional[str] = None,
        toml: Optional[str] = None,
        default: Any = None,
    ):
        self.name: Optional[str] = None
        self.env = env
        self.toml = toml
        self.default = default

    def __set_name__(self, owner: type, name: str) -> None:
        """Store the attribute name for type conversion."""
        self.name = name

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the ConfField to the dictionary format expected by BaseConfig.

        Returns:
            A dict with keys: env, toml, default, name
        """
        return {
            "env": self.env,
            "toml": self.toml,
            "default": self.default,
            "name": self.name,
        }

    def convert_value(self, value: Any) -> Any:
        """
        Convert the raw value to the appropriate type based on field name.

        Args:
            value: Raw value from env or TOML

        Returns:
            Converted value of the appropriate type
        """
        # Handle None values with sensible defaults
        if value is None:
            if self.name in self.BOOL_FIELDS:
                return False
            if self.name in self.LIST_FIELDS:
                return []
            return ""

        # Handle boolean fields
        if self.name in self.BOOL_FIELDS:
            return to_bool(value)

        # Handle list fields
        if self.name in self.LIST_FIELDS:
            return to_list_of_str(value, str.lower)

        # Default: return as the value's type
        return value

    def __get__(self, instance: Any, owner: type) -> Any:
        """
        This shouldn't be called since BaseConfig converts these to properties.
        """
        if instance is None:
            return self
        raise AttributeError(
            f"{self.__class__.__name__} {self.name} should have been converted to a property"
        )


class Config:
    """Base configuration class that handles loading from environment variables and TOML files."""

    _toml_data: dict[str, Any] = {}
    _config_specs: dict[str, dict[str, Any]] = {}

    @classmethod
    def _get_from_toml(
        cls,
        key: Optional[str],
        default: Any = None,
    ) -> Any:
        """
        Get value from TOML configuration.

        Args:
            key: Dot-separated path to the config value (e.g., "storage.backend")
            default: Default value if key is not found

        Returns:
            The value from TOML, or the default if not found
        """
        if key is None:
            return default

        # Navigate through nested keys
        current = Project.get_toml_section()
        for k in key.split("."):
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default

        return current

    @classmethod
    def _fetch_value(
        cls,
        env_key: Optional[str] = None,
        toml_key: Optional[str] = None,
        default: Any = None,
    ) -> Any:
        """
        Fetch configuration value with fallback priority: ENV -> TOML -> default.

        Args:
            env_key: Environment variable name to check
            toml_key: TOML key path to check (dot-separated)
            default: Default value if neither source has the value

        Returns:
            The configuration value from the first available source (raw, no casting)
        """
        # Try environment variable first (if env_key is provided and exists)
        if env_key is not None and env_key in os.environ:
            return os.environ[env_key]

        # Fall back to TOML config and set default as it is the final fallback
        return cls._get_from_toml(toml_key, default=default)

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
            if not isinstance(attr_value, ConfField):
                continue

            config_dict = attr_value.to_dict()

            # Store the configuration spec for this field
            cls._config_specs[attr_name] = config_dict

            # Create property getter
            def make_getter(name: str, cfg: dict[str, Any], field: ConfField):
                def getter(self: "Config") -> Any:
                    env_key = cfg["env"]
                    toml_key = cfg["toml"]
                    default = cfg["default"]
                    raw_value = self._fetch_value(env_key, toml_key, default)

                    # Convert to the appropriate type
                    return field.convert_value(raw_value)

                return getter

            setattr(
                cls,
                attr_name,
                property(make_getter(attr_name, config_dict, attr_value)),
            )

    @classmethod
    def list_env_keys(cls) -> list[str]:
        """List all environment variable keys used by this config class."""
        return [
            spec["env"]
            for spec in cls._config_specs.values()
            if spec.get("env") is not None
        ]

    @classmethod
    def get_env_var_info(cls) -> list[dict[str, Any]]:
        """
        Get detailed information about all environment variables in this config class.

        Returns:
            List of dictionaries containing:
                - env_key: Environment variable name
                - toml_key: Corresponding TOML key path
                - default: Default value if any
                - name: Field name in the config class
        """
        vars_info: list[dict[str, Any]] = []

        for var_name, spec in cls._config_specs.items():
            env_key = spec.get("env")
            if env_key:  # Only include if it has an env key
                vars_info.append(
                    {
                        "env_key": env_key,
                        "toml_key": spec.get("toml"),
                        "default": spec.get("default"),
                        "name": var_name,
                    }
                )

        return vars_info
