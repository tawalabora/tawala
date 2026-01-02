from typing import TYPE_CHECKING

from django import template
from django.conf import settings
from django.templatetags.static import static

from tawala.management.types import OrgKey

if TYPE_CHECKING:
    from tawala.management.settings.base import OrgConf

register = template.Library()


@register.simple_tag
def org(key: OrgKey) -> str:
    """Return the organization name from settings."""
    try:
        org_conf: "OrgConf" = settings.ORG
        org_key = key.lower().replace("-", "_")

        match org_key:
            case "logo_url" | "favicon_url" | "apple_touch_icon_url":
                return static(getattr(org_conf, org_key, ""))
            case _:
                return getattr(org_conf, org_key, "")

    except (AttributeError, KeyError):
        return ""
