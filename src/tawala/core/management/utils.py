from typing import Any, Iterable, Tuple


def calculate_max_length_from_choices(choices: Iterable[Tuple[str, Any]]) -> int:
    """
    Utility function to get the max_length for a CharField based on the longest choice value.

    Args:
        choices: A tuple of choices

    Example:
        class MyModel(models.Model):
            class Choices(models.TextChoices):
                SHORT = "SHORT", "Short Option"
                VERY_LONG_OPTION = "VERY_LONG_OPTION", "Very Long Option"

            field = models.CharField(
                max_length=calculate_max_length_from_choices(Choices.choices),
                choices=Choices.choices
            )

    Returns:
        int: The length of the longest choice value.
    """
    return max(len(choice[0]) for choice in choices)


def to_bool(value: Any) -> bool:
    """
    Convert a value to boolean.

    Args:
        value: The value to convert.

    Returns:
        bool: The converted boolean value.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes", "on")
    return bool(value)


def to_list_of_str(value: Any, transform: callable = None) -> list[str]:
    """
    Convert a value to a list of strings, with optional transformation.

    Args:
        value: The value to convert.
        transform: Optional function to apply to each string (e.g., str.lower).

    Returns:
        list[str]: The converted list of strings.
    """
    if isinstance(value, list):
        result = [str(item) for item in value]
    elif isinstance(value, str):
        result = [item.strip() for item in value.split(",") if item.strip()]
    else:
        return []
    if transform:
        result = [transform(item) for item in result]
    return result


def to_str_if_value_else_empty_str(value: Any, transform: callable = None) -> str:
    """
    Ensure the value is a string, with optional transformation.

    Args:
        value: The value to convert.
        transform: Optional function to apply to the string (e.g., str.lower).

    Returns:
        str: The converted string value.
    """
    if isinstance(value, str):
        result = value
    else:
        result = str(value) if value else ""
    if transform and result:
        result = transform(result)
    return result
