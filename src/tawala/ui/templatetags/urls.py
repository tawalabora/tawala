from django.conf import settings
from django.template import Library

register = Library()


@register.simple_tag
def home_url() -> str:
    """Get the home URL."""

    return settings.HOME_URL


@register.simple_tag
def admin_url() -> str:
    """Get the admin URL."""

    return settings.ADMIN_URL


@register.simple_tag
def static_url() -> str:
    """Get the static URL."""

    return settings.STATIC_URL


@register.simple_tag
def media_url() -> str:
    """Get the media URL."""

    return settings.MEDIA_URL


@register.simple_tag
def browser_reload_url() -> str:
    """Get the browser reload URL."""

    return settings.BROWSER_RELOAD_URL
