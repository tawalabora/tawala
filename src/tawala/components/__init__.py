from django.conf import settings

# TODO: Implement a test or a system checkup that's used by to be part of those system checks done by Django to ensure that SETTING in `getattr(settings, [SETTING])` match in settings.py

PKG_NAME_SETTING = getattr(settings, "PKG_NAME")
PKG_DIR_SETTING = getattr(settings, "PKG_DIR")
PKG_VERSION_SETTING = getattr(settings, "PKG_VERSION")
BASE_DIR_SETTING = getattr(settings, "BASE_DIR")
TAILWIND_CLI_SETTING = getattr(settings, "TAILWIND_CLI")
STORAGE_TOKEN_SETTING = getattr(settings, "STORAGE_TOKEN")
COMMANDS_BUILD_SETTING = getattr(settings, "COMMANDS_BUILD")
COMMANDS_INSTALL_SETTING = getattr(settings, "COMMANDS_INSTALL")
LOGIN_REDIRECT_URL_SETTING = getattr(settings, "LOGIN_REDIRECT_URL", "/")


__all__ = [
    "PKG_NAME_SETTING",
    "PKG_DIR_SETTING",
    "PKG_VERSION_SETTING",
    "BASE_DIR_SETTING",
    "TAILWIND_CLI_SETTING",
    "STORAGE_TOKEN_SETTING",
    "COMMANDS_BUILD_SETTING",
    "COMMANDS_INSTALL_SETTING",
    "LOGIN_REDIRECT_URL_SETTING",
]
