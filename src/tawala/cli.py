#!/usr/bin/env python

from os import environ
from sys import argv, exit, path
from typing import NoReturn, Optional

from christianwhocodes.helpers import ExitCode, Version
from christianwhocodes.stdout import print
from django.core.management import ManagementUtility

from . import DJANGO_SETTINGS_MODULE, PACKAGE, PROJECT_ROOT


def main() -> Optional[NoReturn]:
    f"""Main entry point for the {PACKAGE.name.capitalize()} CLI."""

    match argv[1]:
        case "-v" | "--version" | "version":
            if PACKAGE.version != Version.placeholder():
                print(PACKAGE.version)
                exit(ExitCode.SUCCESS)
            else:
                print(f"{PACKAGE.version}: Could not determine {PACKAGE.name} version.")
                exit(ExitCode.ERROR)

        case _:
            path.insert(0, str(PROJECT_ROOT.dir))
            environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS_MODULE)

            utility = ManagementUtility(argv)
            utility.prog_name = PACKAGE.name
            utility.execute()


if __name__ == "__main__":
    main()
