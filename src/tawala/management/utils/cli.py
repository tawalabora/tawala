#!/usr/bin/env python

import sys
from typing import NoReturn, Optional

from .constants import DJANGO_SETTINGS_MODULE, TAWALA


def main() -> Optional[NoReturn]:
    f"""Main entry point for the {TAWALA.capitalize()} CLI."""
    match sys.argv[1]:
        case "-v" | "--version" | "version":
            from christianwhocodes.helpers.version import print_version

            sys.exit(print_version(TAWALA))

        case _:
            from os import environ
            from pathlib import Path

            from django.core.management import ManagementUtility

            sys.path.insert(0, str(Path.cwd()))
            environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS_MODULE)

            utility = ManagementUtility(sys.argv)
            utility.prog_name = TAWALA
            utility.execute()


if __name__ == "__main__":
    main()
