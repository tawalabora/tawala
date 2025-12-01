from typing import Any, Callable, Iterable, Optional, Tuple, cast


def calculate_max_length_from_choices(choices: Iterable[Tuple[str, Any]]) -> int:
    """
    Utility function to get the max_length for a tuple of choices

    Args:
        choices: A tuple of choices

    Returns:
        int: The length of the longest choice value.
    """
    return max(len(choice[0]) for choice in choices)


def to_bool(value: str | bool) -> bool:
    """Confirms a boolean value or converts a 'true' / '1' / 'yes' / 'on' string to bool

    Args:
        value (str | bool): string or bool value to be converted

    Returns:
        bool: Returned value
    """
    if isinstance(value, bool):
        return value
    return value.lower() in ("true", "1", "yes", "on")


def to_list_of_str(
    value: Any, transform: Optional[Callable[[str], str]] = None
) -> list[str]:
    """
    Convert a value to a list of strings, with optional transformation.

    Args:
        value: The value to convert.
        transform: Optional function to apply to each string (e.g., str.lower).

    Returns:
        list[str]: The converted list of strings.
    """
    result: list[str] = []

    if isinstance(value, list):
        # Cast to list[Any] to help type checker understand iteration
        list_value = cast(list[Any], value)
        result = [str(item) for item in list_value]
    elif isinstance(value, str):
        result = [item.strip() for item in value.split(",") if item.strip()]

    if transform:
        result = [transform(item) for item in result]

    return result
