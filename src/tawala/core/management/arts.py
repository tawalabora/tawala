"""ASCII art management for Tawala management commands.

Provides centralized ASCII art rendering for various commands with
terminal-responsive designs that adapt to terminal width.
"""

from .enums import TerminalSize


def get_tawala_art(terminal_width: int) -> list[str]:
    """Get Tawala ASCII art based on terminal width.

    Args:
        terminal_width: The width of the terminal in columns.

    Returns:
        List of strings representing the ASCII art lines.
    """
    if terminal_width >= TerminalSize.THRESHOLD:
        return [
            "",
            "  ████████╗ █████╗ ██╗    ██╗ █████╗ ██╗      █████╗ ",
            "  ╚══██╔══╝██╔══██╗██║    ██║██╔══██╗██║     ██╔══██╗",
            "     ██║   ███████║██║ █╗ ██║███████║██║     ███████║",
            "     ██║   ██╔══██║██║███╗██║██╔══██║██║     ██╔══██║",
            "     ██║   ██║  ██║╚███╔███╔╝██║  ██║███████╗██║  ██║",
            "     ╚═╝   ╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝",
            "",
        ]
    else:
        return [
            "",
            "  ▀█▀ ▄▀█ █░█░█ ▄▀█ █░░ ▄▀█",
            "  ░█░ █▀█ ▀▄▀▄▀ █▀█ █▄▄ █▀█",
            "",
        ]


def get_dev_art(terminal_width: int) -> list[str]:
    """Get Dev server ASCII art based on terminal width.

    Args:
        terminal_width: The width of the terminal in columns.

    Returns:
        List of strings representing the ASCII art lines.
    """
    tawala_art = get_tawala_art(terminal_width)

    if terminal_width >= TerminalSize.THRESHOLD:
        dev_art = [
            "        ██████╗ ███████╗██╗   ██╗",
            "        ██╔══██╗██╔════╝██║   ██║",
            "        ██║  ██║█████╗  ██║   ██║",
            "        ██║  ██║██╔══╝  ╚██╗ ██╔╝",
            "        ██████╔╝███████╗ ╚████╔╝ ",
            "        ╚═════╝ ╚══════╝  ╚═══╝  ",
            "",
        ]
    else:
        dev_art = [
            "       █▀▄ █▀▀ █░█",
            "       █▄▀ ██▄ ▀▄▀",
            "",
        ]

    return tawala_art + dev_art


def get_build_art(terminal_width: int) -> list[str]:
    """Get Build ASCII art based on terminal width.

    Args:
        terminal_width: The width of the terminal in columns.

    Returns:
        List of strings representing the ASCII art lines.
    """
    tawala_art = get_tawala_art(terminal_width)

    if terminal_width >= TerminalSize.THRESHOLD:
        build_art = [
            "        ██████╗ ██╗   ██╗██╗██╗     ██████╗ ",
            "        ██╔══██╗██║   ██║██║██║     ██╔══██╗",
            "        ██████╔╝██║   ██║██║██║     ██║  ██║",
            "        ██╔══██╗██║   ██║██║██║     ██║  ██║",
            "        ██████╔╝╚██████╔╝██║███████╗██████╔╝",
            "        ╚═════╝  ╚═════╝ ╚═╝╚══════╝╚═════╝ ",
            "",
        ]
    else:
        build_art = [
            "       █▄▄ █░█ █ █░░ █▀▄",
            "       █▄█ █▄█ █ █▄▄ █▄▀",
            "",
        ]

    return tawala_art + build_art
