import builtins
import pathlib
from typing import Any, Literal, Optional, cast

from christianwhocodes.helpers import TypeConverter
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .project import PROJECT


class ConfField:
    """
    Configuration field descriptor.

    This class defines a configuration field that can be populated from either
    environment variables or TOML configuration files.

    Args:
        env: Environment variable name to read from
        toml: TOML key path (dot-separated) to read from
        type: Type to convert the value to. Supports:
            - str, bool, pathlib.Path
            - "email" for validated email strings
            - list[str] for list of strings
            - list["email"] for list of validated emails
    """

    def __init__(
        self,
        env: Optional[str] = None,
        toml: Optional[str] = None,
        type: (
            type[str]
            | type[bool]
            | type[list[str]]
            | type[pathlib.Path]
            | Literal["email"]
            | Literal["list[str]"]
            | Literal["list[email]"]
        ) = str,
    ):
        self.name: Optional[str] = None
        self.env = env
        self.toml = toml
        self.type = type

    def __set_name__(self, owner: type, name: str) -> None:
        """Store the attribute name for type conversion."""
        self.name = name

    @property
    def dict(self) -> dict[str, Any]:
        """
        Convert the ConfField to the dictionary format expected by BaseConfig.

        Returns:
            A dict with keys: env, toml, name, type
        """
        return {
            "env": self.env,
            "toml": self.toml,
            "name": self.name,
            "type": self.type,
        }

    @staticmethod
    def validate_email_value(value: Any) -> str:
        """
        Validate a single email address using Django's validator.

        Args:
            value: Email address to validate

        Returns:
            The validated email string

        Raises:
            ValueError: If the email is invalid
        """
        if value is None or value == "":
            return ""

        email_str = str(value).strip()
        try:
            validate_email(email_str)
            return email_str
        except ValidationError as e:
            raise ValueError(f"Invalid email address '{email_str}': {e.message}")

    @staticmethod
    def parse_list_type(type_spec: Any) -> tuple[bool, Optional[str]]:
        """
        Parse a type specification to determine if it's a list and what the item type is.

        Args:
            type_spec: Type specification (e.g., list[str], "list[email]", list)

        Returns:
            Tuple of (is_list, item_type) where item_type is "str", "email", or None
        """
        # Handle string type specifications like "list[str]" or "list[email]"
        if isinstance(type_spec, str):
            if type_spec.startswith("list[") and type_spec.endswith("]"):
                item_type = type_spec[5:-1]  # Extract content between "list[" and "]"
                return (True, item_type)
            return (False, None)

        # Handle actual type objects like list[str]
        if type_spec is builtins.list:
            return (True, "str")  # Default to str for backwards compatibility

        return (False, None)

    @staticmethod
    def convert_value(value: Any, target_type: Any) -> Any:
        """
        Convert the raw value to the appropriate type.

        Args:
            value: Raw value from env or TOML
            target_type: The type to convert to

        Returns:
            Converted value of the appropriate type
        """
        # Parse if this is a list type
        is_list, item_type = ConfField.parse_list_type(target_type)

        # Handle None values
        if value is None:
            if is_list:
                return []
            elif target_type == "email" or target_type is str:
                return ""
            else:
                return None

        # Handle list types
        if is_list:
            # Convert to list of strings first
            string_list = TypeConverter.to_list_of_str(value, str.strip)

            # Then validate/convert each item based on item_type
            if item_type == "email":
                validated_emails: list[str] = []
                for email in string_list:
                    if email:  # Skip empty strings
                        validated_emails.append(ConfField.validate_email_value(email))
                return validated_emails
            else:  # item_type == "str" or None (default to str)
                return string_list

        # Handle scalar types
        match target_type:
            case builtins.bool:
                return TypeConverter.to_bool(value)
            case pathlib.Path:
                return TypeConverter.to_path(value)
            case builtins.str:
                return str(value)
            case "email":
                return ConfField.validate_email_value(value)
            case _:
                raise ValueError(f"Unsupported target type: {target_type}")

    def __get__(self, instance: Any, owner: type) -> Any:
        """
        This shouldn't be called since BaseConfig converts these to properties.
        """
        if instance is None:
            return self
        raise AttributeError(
            f"{self.__class__.__name__} {self.name} should have been converted to a property"
        )


class Conf:
    """Base configuration class that handles loading from environment variables and TOML files."""

    # Track all Conf subclasses
    _subclasses: list[type["Conf"]] = []

    @staticmethod
    def _get_from_toml(key: Optional[str]) -> Any:
        """
        Get value from TOML configuration.

        Args:
            key: Dot-separated path to the config value (e.g., "storage.backend")

        Returns:
            The value from TOML, or None if not found
        """

        if key is None:
            return None
        else:
            current: Any = PROJECT["toml"]
            for k in key.split("."):
                if isinstance(current, dict) and k in current:
                    current = cast(Any, current[k])
                else:
                    return None

            return current

    @classmethod
    def _fetch_value(
        cls,
        env_key: Optional[str] = None,
        toml_key: Optional[str] = None,
    ) -> Any:
        """
        Fetch configuration value with fallback priority: ENV -> TOML -> None.

        Args:
            env_key: Environment variable name to check
            toml_key: TOML key path to check (dot-separated)

        Returns:
            The configuration value from the first available source (raw, no casting)
        """
        # Try environment variable first (if env_key is provided and exists)
        env_config = PROJECT["env"]
        if env_key is not None and env_key in env_config:
            return env_config[env_key]

        # Else fall back to TOML config and set None as it is the final fallback
        else:
            return cls._get_from_toml(toml_key)

    def __init_subclass__(cls) -> None:
        """
        Automatically convert ConfField descriptors to properties
        when a subclass is created.
        """
        super().__init_subclass__()

        # Register this subclass
        Conf._subclasses.append(cls)

        # Initialize _env_fields for this subclass
        if not hasattr(cls, "_env_fields"):
            cls._env_fields: list[dict[str, Any]] = []

        for attr_name, attr_value in list(vars(cls).items()):
            # Skip private attributes, methods, and special descriptors
            if (
                attr_name.startswith("_")
                or callable(attr_value)
                or isinstance(attr_value, (classmethod, staticmethod, property))
            ):
                continue

            # Check if this is a ConfField
            if not isinstance(attr_value, ConfField):
                continue

            config_dict = attr_value.dict

            # Store field metadata if it has an env key
            if config_dict["env"] is not None:
                cls._env_fields.append(
                    {
                        "env": config_dict["env"],
                        "toml": config_dict["toml"],
                        "name": config_dict["name"],
                        "type": config_dict["type"],
                        "class": cls.__name__,
                    }
                )

            # Create property getter
            def make_getter(name: str, cfg: dict[str, Any]):
                def getter(self: "Conf") -> Any:
                    env_key = cfg["env"]
                    toml_key = cfg["toml"]
                    target_type = cfg["type"]
                    raw_value = self._fetch_value(env_key, toml_key)

                    # Convert to the appropriate type
                    return ConfField.convert_value(raw_value, target_type)

                return getter

            setattr(
                cls,
                attr_name,
                property(make_getter(attr_name, config_dict)),
            )

    @classmethod
    def get_all_env_fields(cls) -> list[dict[str, Any]]:
        """
        Collect all ConfField definitions that use environment variables
        from all Conf subclasses.

        Returns:
            List of dicts containing env key, toml key, name, type, and class for each field
        """
        env_fields: list[dict[str, Any]] = []

        for subclass in cls._subclasses:
            if hasattr(subclass, "_env_fields"):
                env_fields.extend(subclass._env_fields)

        return env_fields
