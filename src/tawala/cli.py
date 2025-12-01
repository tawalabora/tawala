#!/usr/bin/env python
"""
Tawala CLI.

Provides the management commands interface for Tawala.
"""

import os
import sys
from typing import NoReturn, Optional

from django.core.management import ManagementUtility

from .conf.base import Project
from .conf.checks import CLISetup


def main() -> Optional[NoReturn]:
    """Main entry point for the Tawala CLI."""

    match sys.argv[1]:
        case "-v" | "--version" | "version":
            from importlib.metadata import version

            print(version("tawala"))
            sys.exit(0)

        case _:
            pass

    base_dir = Project.get_base_dir_or_exit()
    sys.path.insert(0, str(base_dir))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tawala.conf.settings")
    CLISetup.setsuccessful()

    utility = ManagementUtility(sys.argv)
    utility.prog_name = "tawala"
    utility.execute()


if __name__ == "__main__":
    main()
