#!/usr/bin/env python

import sys
from typing import NoReturn, Optional


def main() -> Optional[NoReturn]:
    f"""Main entry point for the {"tawala".capitalize()} CLI."""

    match sys.argv[1]:
        case "-v" | "--version" | "version":
            from ..utils.helpers import print_version

            sys.exit(print_version())

        case _:
            from os import environ
            from pathlib import Path

            from django.core.management import ManagementUtility

            sys.path.insert(0, str(Path.cwd()))
            environ.setdefault("DJANGO_SETTINGS_MODULE", "tawala.management.settings")

            utility = ManagementUtility(sys.argv)
            utility.prog_name = "tawala"
            utility.execute()


if __name__ == "__main__":
    main()
