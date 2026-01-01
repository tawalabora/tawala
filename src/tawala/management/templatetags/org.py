from pathlib import Path
from typing import TYPE_CHECKING

from django import template
from django.conf import settings
from django.templatetags.static import static

from ..types import OrgKey

if TYPE_CHECKING:
    from ..settings.org import OrgConf

register = template.Library()


@register.simple_tag
def org(key: OrgKey) -> str:
    """Return the organization name from settings."""
    try:
        org_conf: "OrgConf" = settings.ORG
        org_key = key.lower().replace("-", "_")
        return getattr(org_conf, org_key, "")
    except (AttributeError, KeyError):
        return ""


class StaticAssetResolver:
    """Helper class to resolve static asset URLs."""

    @staticmethod
    def get_asset_url(relative_path: str, fallback_path: str) -> str:
        """Get the URL for a static asset.

        Args:
            relative_path: Path to the asset relative to app_dir/static
            fallback_path: Fallback path relative to static directory

        Returns:
            The static URL for the asset or fallback
        """
        expected_asset = Path.cwd() / settings.MAIN_INSTALLED_APP / "static" / relative_path

        if expected_asset.exists() and expected_asset.is_file():
            return static(relative_path)
        else:
            return static(fallback_path)


@register.simple_tag
def org_logo_url() -> str:
    """Return the organization logo URL from settings.

    Returns:
        The organization logo URL
    """
    return StaticAssetResolver.get_asset_url(
        relative_path=f"{settings.MAIN_INSTALLED_APP}/logo.png",
        fallback_path="core/logo.png",
    )


@register.simple_tag
def org_favicon_url() -> str:
    """Return the organization favicon URL from settings.

    Returns:
        The organization favicon URL
    """
    return StaticAssetResolver.get_asset_url(
        relative_path=f"{settings.MAIN_INSTALLED_APP}/favicon.ico",
        fallback_path="core/favicon.ico",
    )


@register.simple_tag
def org_apple_touch_icon_url() -> str:
    """Return the organization Apple Touch Icon URL from settings.

    Returns:
        The organization Apple Touch Icon URL
    """
    return StaticAssetResolver.get_asset_url(
        relative_path=f"{settings.MAIN_INSTALLED_APP}/apple-touch-icon.png",
        fallback_path="core/apple-touch-icon.png",
    )
