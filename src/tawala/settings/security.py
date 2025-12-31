from typing import NotRequired, TypedDict, Optional

from .conf import Conf, ConfField


class SecurityConf(Conf):
    """Security-related configuration settings."""

    secret_key = ConfField(env="SECRET_KEY", toml="secret-key", type=str)
    debug = ConfField(env="DEBUG", toml="debug", type=bool)
    allowed_hosts = ConfField(env="ALLOWED_HOSTS", toml="allowed-hosts", type="list[str]")


_security = SecurityConf()


class SecuritySettingsDict(TypedDict):
    """Type definition for security settings."""

    SECRET_KEY: str
    DEBUG: bool
    ALLOWED_HOSTS: list[str]
    SECURE_SSL_REDIRECT: NotRequired[bool]
    SESSION_COOKIE_SECURE: NotRequired[bool]
    CSRF_COOKIE_SECURE: NotRequired[bool]
    # SECURE_HSTS_SECONDS: NotRequired[int]


# ==============================================================================
# Security & deployment checklist
# See https://docs.djangoproject.com/en/stable/howto/deployment/checklist/
# ==============================================================================


def _get_security_settings() -> SecuritySettingsDict:
    """Generate security settings based on DEBUG mode."""

    settings: SecuritySettingsDict = {
        "SECRET_KEY": _security.secret_key,
        "DEBUG": _security.debug,
        "ALLOWED_HOSTS": _security.allowed_hosts,
    }

    # Production security settings
    if not _security.debug:
        settings["SECURE_SSL_REDIRECT"] = True
        settings["SESSION_COOKIE_SECURE"] = True
        settings["CSRF_COOKIE_SECURE"] = True
        # settings["SECURE_HSTS_SECONDS"] = 3600

    return settings


_settings = _get_security_settings()

SECRET_KEY: str = _settings["SECRET_KEY"]
DEBUG: bool = _settings["DEBUG"]
ALLOWED_HOSTS: list[str] = _settings["ALLOWED_HOSTS"]
SECURE_SSL_REDIRECT: Optional[bool] = _settings.get("SECURE_SSL_REDIRECT")
SESSION_COOKIE_SECURE: Optional[bool] = _settings.get("SESSION_COOKIE_SECURE")
CSRF_COOKIE_SECURE: Optional[bool] = _settings.get("CSRF_COOKIE_SECURE")
# SECURE_HSTS_SECONDS: Optional[int] = _settings.get("SECURE_HSTS_SECONDS")


__all__ = [
    "SECRET_KEY",
    "DEBUG",
    "ALLOWED_HOSTS",
    "SECURE_SSL_REDIRECT",
    "SESSION_COOKIE_SECURE",
    "CSRF_COOKIE_SECURE",
    # "SECURE_HSTS_SECONDS",
]
