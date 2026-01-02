from christianwhocodes.helpers.urls import normalize_url_path

from .conf import Conf, ConfField


class UrlPatternsConf(Conf):
    """URL-related configuration settings."""

    home = ConfField(env="URLS_HOME", toml="urls.home", default="/", type=str)
    admin = ConfField(env="URLS_ADMIN", toml="urls.admin", default="admin/", type=str)
    static = ConfField(env="URLS_STATIC", toml="urls.static", default="static/", type=str)
    media = ConfField(env="URLS_MEDIA", toml="urls.media", default="media/", type=str)
    browser_reload = ConfField(
        env="URLS_BROWSER_RELOAD",
        toml="urls.browser_reload",
        default="__reload__/",
        type=str,
    )


_URLPATTERNS = UrlPatternsConf()

HOME_URL: str = "/" if _URLPATTERNS.home == "/" else normalize_url_path(_URLPATTERNS.home)
ADMIN_URL: str = normalize_url_path(_URLPATTERNS.admin)
STATIC_URL: str = normalize_url_path(_URLPATTERNS.static)
MEDIA_URL: str = normalize_url_path(_URLPATTERNS.media)
BROWSER_RELOAD_URL: str = normalize_url_path(_URLPATTERNS.browser_reload)


__all__ = ["HOME_URL", "ADMIN_URL", "STATIC_URL", "MEDIA_URL", "BROWSER_RELOAD_URL"]
