from pathlib import Path

from django import template
from django.template import Context
from django.templatetags.static import static
from django.utils.safestring import SafeString, mark_safe

from ... import TAILWIND_CLI_SETTING

register = template.Library()


@register.simple_tag(takes_context=True)
def page_title(
    context: Context, name: str | None = None, separator: str = " | "
) -> SafeString:
    """
    Generate a complete HTML `<title>` tag combining page title and site name.

    Creates a properly formatted `<title>` element that combines a page-specific
    title with the site name from environment configuration. The title follows
    the pattern: "Page Title | Site Name" or just "Site Name" if no page title.

    Args:
        context: Django template context (automatically passed)
        name: Optional page title. If not provided, uses context['page_title']
        separator: String to separate page title and site name (default: " | ")

    Returns:
        SafeString containing the complete HTML `<title>` tag

    Usage:
        {% page_title %}                        ← "Site Name" or "Page Title | Site Name"
        {% page_title "Custom Page" %}          ← "Custom Page | Site Name"
        {% page_title "Custom Page" " - " %}    ← "Custom Page - Site Name"
        {% page_title separator=" :: " %}       ← "Page Title :: Site Name"

    Note:
        Requires SITE_NAME setting to be set for the site name portion.
    """
    site_name = ""
    title = name or context.get("page_title")

    full_title = (
        f"{title}{separator if site_name else ''}{site_name}" if title else site_name
    )
    return mark_safe(f"<title>{full_title}</title>")


@register.simple_tag(takes_context=True)
def tailwindcss(context: Context) -> SafeString:
    """
    Load Tailwind CSS from compiled output if present,
    otherwise fall back to Tailwind Play CDN.

    When using the CDN fallback, a CSP nonce is injected
    via a meta tag for compatibility with strict CSP.
    """

    input_css: Path = TAILWIND_CLI_SETTING["CSS"]["input"]
    output_css: Path = TAILWIND_CLI_SETTING["CSS"]["output"]

    # ------------------------------------------------------------------
    # 1. Use Tailwind css input if it exists and watch for file changes.
    # ------------------------------------------------------------------
    if input_css.exists() and input_css.is_file():
        # TODO: Implement logic for watching for changes. Leave the management command for building as it it. Here in this templatetag, we will only be watching.
        output_static_dir = output_css.parent

        while (
            output_static_dir.name != "static"
            and output_static_dir != output_static_dir.parent
        ):
            output_static_dir = output_static_dir.parent

        if output_static_dir.name == "static":
            relative_path = output_css.relative_to(output_static_dir)
            static_url = static(str(relative_path))
        else:
            static_url = static("ui/css/tailwind.css")

        return mark_safe(f"<link rel='stylesheet' href='{static_url}' />")

    # ------------------------------------------------------------------
    # 2. Local Tailwind Play CDN copy fallback
    # ------------------------------------------------------------------

    tailwind_cdn_url = static("ui/js/tailwindcss.js")
    return mark_safe(f"<script defer src='{tailwind_cdn_url}'></script>")
