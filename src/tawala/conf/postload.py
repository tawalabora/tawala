"""Post app initialization

These settings are used throughout ui and utils post initialization,
Centralized here for easy management, ensuring that they are gotten from django.conf instead of own customized settings.py.

Note the order:
- `preload.py` configures `config.py`, which in turns is used to configure `settings.py`.
- `preload.py` is used to load settings from `pyproject.toml` and passes it to `config.py`.
- `config.py` chooses the which configurations - either from .env, pyproject.toml, or default - to settle on, 
- and then passes on the configs to `settings.py`.
- `settings.py` is then loaded by Django, from which, in `postload.py`,
- we centralize the variables that are used within core and components for easy tracking and management.
"""

from django.conf import settings


# TODO: Implement a test or a system checkup that's used by to be part of those system checks done by Django to ensure that SETTING in `getattr(settings, [SETTING])` match in settings.py

PKG_NAME = getattr(settings, "PKG_NAME")
PKG_DIR = getattr(settings, "PKG_DIR")
PKG_VERSION = getattr(settings, "PKG_VERSION")
BASE_DIR = getattr(settings, "BASE_DIR")
CLI_DIR = getattr(settings, "CLI_DIR")
TAILWIND_CLI = getattr(settings, "TAILWIND_CLI")
STORAGE_TOKEN = getattr(settings, "STORAGE_TOKEN")
COMMANDS_BUILD = getattr(settings, "COMMANDS_BUILD")
COMMANDS_INSTALL = getattr(settings, "COMMANDS_INSTALL")
LOGIN_REDIRECT_URL = getattr(settings, "LOGIN_REDIRECT_URL", "/")
