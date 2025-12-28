from typing import Optional

from django import template
from django.template import Context
from django.utils.safestring import SafeString, mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def title(context: Context, name: Optional[str] = None, separator: str = " | ") -> SafeString:
    """
    Generate a complete HTML `<title>` tag combining page title and site name.

    Creates a properly formatted `<title>` element that combines a page-specific
    title with the site name from environment configuration. The title follows
    the pattern: "Page Title | Site Name" or just "Site Name" if no page title.

    Args:
        context: Django template context (automatically passed)
        name: Optional page title. If not provided, uses context['title']
        separator: String to separate page title and site name (default: " | ")

    Returns:
        SafeString containing the complete HTML `<title>` tag

    Usage:
        {% title %}                        ← "Site Name" or "Page Title | Site Name"
        {% title "Custom Page" %}          ← "Custom Page | Site Name"
        {% title "Custom Page" " - " %}    ← "Custom Page - Site Name"
        {% title separator=" :: " %}       ← "Custom Page :: Site Name"

    Note:
        Requires SITE_NAME setting to be set for the site name portion.
    """
    site_name: str = ""
    title_text: Optional[str] = name or context.get("title")

    full_title: str = (
        f"{title_text}{separator if site_name else ''}{site_name}" if title_text else site_name
    )
    return mark_safe(f"<title>{full_title}</title>")
