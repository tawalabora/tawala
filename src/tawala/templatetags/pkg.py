from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def pkg_name() -> str:
    """Returns the package name."""
    return settings.PKG["name"]
