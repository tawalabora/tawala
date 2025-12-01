from enum import IntEnum


class TerminalSize(IntEnum):
    """Terminal size threshold for ASCII art.

    Used to determine whether to display the full ASCII banner or a compact version.

    Attributes:
        THRESHOLD: Minimum terminal width (in columns) required for full ASCII art.
    """

    THRESHOLD = 60
