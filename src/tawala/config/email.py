from typing import TypedDict

from .conf import Conf, ConfField


class EmailConf(Conf):
    """Email configuration settings."""

    backend = ConfField(env="EMAIL_BACKEND", toml="email.backend", type=str)
    host = ConfField(env="EMAIL_HOST", toml="email.host", type=str)
    port = ConfField(env="EMAIL_PORT", toml="email.port", type=str)
    use_tls = ConfField(env="EMAIL_USE_TLS", toml="email.use-tls", type=bool)
    host_user = ConfField(env="EMAIL_HOST_USER", toml="email.host-user", type=str)
    host_password = ConfField(env="EMAIL_HOST_PASSWORD", toml="email.host-password", type=str)


_email = EmailConf()


class EmailConfigDict(TypedDict):
    """Type definition for email configuration."""

    EMAIL_BACKEND: str
    EMAIL_HOST: str
    EMAIL_PORT: str
    EMAIL_USE_TLS: bool
    EMAIL_HOST_USER: str
    EMAIL_HOST_PASSWORD: str


# ==============================================================================
# Email Configuration
# https://docs.djangoproject.com/en/stable/topics/email/
# ==============================================================================


def _get_email_config() -> EmailConfigDict:
    """Generate email configuration dictionary."""
    return {
        "EMAIL_BACKEND": _email.backend,
        "EMAIL_HOST": _email.host,
        "EMAIL_PORT": _email.port,
        "EMAIL_USE_TLS": _email.use_tls,
        "EMAIL_HOST_USER": _email.host_user,
        "EMAIL_HOST_PASSWORD": _email.host_password,
    }


_email_config = _get_email_config()

EMAIL_BACKEND: str = _email_config["EMAIL_BACKEND"]
EMAIL_HOST: str = _email_config["EMAIL_HOST"]
EMAIL_PORT: str = _email_config["EMAIL_PORT"]
EMAIL_USE_TLS: bool = _email_config["EMAIL_USE_TLS"]
EMAIL_HOST_USER: str = _email_config["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD: str = _email_config["EMAIL_HOST_PASSWORD"]


__all__ = [
    "EMAIL_BACKEND",
    "EMAIL_HOST",
    "EMAIL_PORT",
    "EMAIL_USE_TLS",
    "EMAIL_HOST_USER",
    "EMAIL_HOST_PASSWORD",
]
