from typing import TypedDict

from .conf import Conf, ConfField


class CommandsConf(Conf):
    """Install/Build Commands to be executed settings."""

    install = ConfField(env="COMMANDS_INSTALL", toml="commands.install", type="list[str]")
    build = ConfField(env="COMMANDS_BUILD", toml="commands.build", type="list[str]")


class CommandsDict(TypedDict):
    """Type definition for Commands configuration dictionary."""

    install: list[str]
    build: list[str]


_commands = CommandsConf()

COMMANDS: CommandsDict = {
    "install": _commands.install,
    "build": _commands.build
    or [
        "makemigrations",
        "migrate",
        "tailwindcss build",
        "collectstatic --noinput",
    ],
}

__all__ = ["COMMANDS"]
