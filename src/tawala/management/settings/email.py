# ==============================================================================
# Email Configuration
# https://docs.djangoproject.com/en/stable/topics/email/
# ==============================================================================
from .conf import Conf, ConfField


class EmailConf(Conf):
    """Email configuration settings."""

    backend = ConfField(env="EMAIL_BACKEND", toml="email.backend", type=str)
    host = ConfField(env="EMAIL_HOST", toml="email.host", type=str)
    port = ConfField(env="EMAIL_PORT", toml="email.port", type=str)
    use_tls = ConfField(env="EMAIL_USE_TLS", toml="email.use-tls", type=bool)
    host_user = ConfField(env="EMAIL_HOST_USER", toml="email.host-user", type=str)
    host_password = ConfField(env="EMAIL_HOST_PASSWORD", toml="email.host-password", type=str)


_EMAIL = EmailConf()

EMAIL_BACKEND: str = _EMAIL.backend
EMAIL_HOST: str = _EMAIL.host
EMAIL_PORT: str = _EMAIL.port
EMAIL_USE_TLS: bool = _EMAIL.use_tls
EMAIL_HOST_USER: str = _EMAIL.host_user
EMAIL_HOST_PASSWORD: str = _EMAIL.host_password


__all__ = [
    "EMAIL_BACKEND",
    "EMAIL_HOST",
    "EMAIL_PORT",
    "EMAIL_USE_TLS",
    "EMAIL_HOST_USER",
    "EMAIL_HOST_PASSWORD",
]
