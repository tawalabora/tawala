from enum import StrEnum

from ..types import TemplatesDict
from .conf import Conf, ConfField


class _App(StrEnum):
    ADMIN = "django.contrib.admin"
    AUTH = "django.contrib.auth"
    CONTENTTYPES = "django.contrib.contenttypes"
    SESSIONS = "django.contrib.sessions"
    MESSAGES = "django.contrib.messages"
    STATICFILES = "django.contrib.staticfiles"
    BROWSER_RELOAD = "django_browser_reload"
    WATCHFILES = "django_watchfiles"
    TAWALA = "tawala"
    TAWALA_MANAGEMENT = "tawala.management"
    TAWALA_CORE = "tawala.core"


class _Middleware(StrEnum):
    SECURITY = "django.middleware.security.SecurityMiddleware"
    SESSION = "django.contrib.sessions.middleware.SessionMiddleware"
    COMMON = "django.middleware.common.CommonMiddleware"
    CSRF = "django.middleware.csrf.CsrfViewMiddleware"
    AUTH = "django.contrib.auth.middleware.AuthenticationMiddleware"
    MESSAGES = "django.contrib.messages.middleware.MessageMiddleware"
    CLICKJACKING = "django.middleware.clickjacking.XFrameOptionsMiddleware"
    CSP = "django.middleware.csp.ContentSecurityPolicyMiddleware"
    BROWSER_RELOAD = "django_browser_reload.middleware.BrowserReloadMiddleware"


class _ContextProcessor(StrEnum):
    CSP = "django.template.context_processors.csp"
    REQUEST = "django.template.context_processors.request"
    AUTH = "django.contrib.auth.context_processors.auth"
    MESSAGES = "django.contrib.messages.context_processors.messages"


# Mapping of apps to their required middleware
_APP_MIDDLEWARE_MAP: dict[_App, list[_Middleware]] = {
    _App.SESSIONS: [_Middleware.SESSION],
    _App.AUTH: [_Middleware.AUTH],
    _App.MESSAGES: [_Middleware.MESSAGES],
    _App.BROWSER_RELOAD: [_Middleware.BROWSER_RELOAD],
}

# Mapping of apps to their required context processors
_APP_CONTEXT_PROCESSOR_MAP: dict[_App, list[_ContextProcessor]] = {
    _App.AUTH: [_ContextProcessor.AUTH],
    _App.MESSAGES: [_ContextProcessor.MESSAGES],
}


class AppsConf(Conf):
    """Apps and middleware configuration settings."""

    main_installed = ConfField(
        env="APPS_MAIN_INSTALLED", toml="apps.main-installed", type=str, default="app"
    )

    extend_installed = ConfField(
        env="APPS_EXTEND_INSTALLED", toml="apps.extend-installed", type=list
    )
    remove_installed = ConfField(
        env="APPS_REMOVE_INSTALLED", toml="apps.remove-installed", type=list
    )
    extend_middleware = ConfField(
        env="APPS_EXTEND_MIDDLEWARE", toml="apps.extend-middleware", type=list
    )
    remove_middleware = ConfField(
        env="APPS_REMOVE_MIDDLEWARE", toml="apps.remove-middleware", type=list
    )
    extend_context_processors = ConfField(
        env="APPS_EXTEND_CONTEXT_PROCESSORS",
        toml="apps.extend-context-processors",
        type=list,
    )
    remove_context_processors = ConfField(
        env="APPS_REMOVE_CONTEXT_PROCESSORS",
        toml="apps.remove-context-processors",
        type=list,
    )


_APPS = AppsConf()

MAIN_INSTALLED_APP = _APPS.main_installed


def _get_installed_apps() -> list[str]:
    base_apps: list[str] = [
        _App.TAWALA,
        _App.TAWALA_MANAGEMENT,
        _App.TAWALA_CORE,
        MAIN_INSTALLED_APP,
    ]

    django_apps: list[str] = [
        _App.ADMIN,
        _App.AUTH,
        _App.CONTENTTYPES,
        _App.SESSIONS,
        _App.MESSAGES,
        _App.STATICFILES,
        _App.BROWSER_RELOAD,
        _App.WATCHFILES,
    ]

    # Collect apps that should be removed except for base apps
    apps_to_remove = [app for app in _APPS.remove_installed if app not in base_apps]

    # Remove apps that are in the remove list
    django_apps = [app for app in django_apps if app not in apps_to_remove]

    # Add custom apps
    all_apps = base_apps + django_apps + _APPS.extend_installed

    # Remove duplicates while preserving order
    return list(dict.fromkeys(all_apps))


def _get_middleware(installed_apps: list[str]) -> list[str]:
    base_middleware: list[str] = [
        _Middleware.SECURITY,
        _Middleware.SESSION,
        _Middleware.COMMON,
        _Middleware.CSRF,
        _Middleware.AUTH,
        _Middleware.MESSAGES,
        _Middleware.CLICKJACKING,
        _Middleware.CSP,
        _Middleware.BROWSER_RELOAD,
    ]

    # Collect middleware that should be removed based on missing apps
    middleware_to_remove: set[str] = set(_APPS.remove_middleware)
    for app, middleware_list in _APP_MIDDLEWARE_MAP.items():
        if app not in installed_apps:
            middleware_to_remove.update(middleware_list)

    # Filter out middleware whose apps are not installed or explicitly removed
    base_middleware = [m for m in base_middleware if m not in middleware_to_remove]

    # Add custom middleware
    all_middleware = base_middleware + _APPS.extend_middleware

    # Remove duplicates while preserving order
    return list(dict.fromkeys(all_middleware))


def _get_context_processors(installed_apps: list[str]) -> list[str]:
    base_context_processors: list[str] = [
        _ContextProcessor.CSP,
        _ContextProcessor.REQUEST,
        _ContextProcessor.AUTH,
        _ContextProcessor.MESSAGES,
    ]

    # Collect context processors that should be removed based on missing apps
    context_processors_to_remove: set[str] = set(_APPS.remove_context_processors)
    for app, processor_list in _APP_CONTEXT_PROCESSOR_MAP.items():
        if app not in installed_apps:
            context_processors_to_remove.update(processor_list)

    # Filter out context processors whose apps are not installed or explicitly removed
    base_context_processors = [
        cp for cp in base_context_processors if cp not in context_processors_to_remove
    ]

    # Add custom context processors
    all_context_processors = base_context_processors + _APPS.extend_context_processors

    # Remove duplicates while preserving order
    return list(dict.fromkeys(all_context_processors))


INSTALLED_APPS: list[str] = _get_installed_apps()
MIDDLEWARE: list[str] = _get_middleware(INSTALLED_APPS)
TEMPLATES: TemplatesDict = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": _get_context_processors(INSTALLED_APPS),
        },
    },
]

ROOT_URLCONF: str = f"{_App.TAWALA_CORE}.urls"
WSGI_APPLICATION: str = f"{_App.TAWALA_CORE}.api.wsgi.application"


__all__ = [
    "MAIN_INSTALLED_APP",
    "INSTALLED_APPS",
    "MIDDLEWARE",
    "TEMPLATES",
    "ROOT_URLCONF",
    "WSGI_APPLICATION",
]
