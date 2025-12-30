from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def get_social_media() -> dict[str, dict[str, str]]:
    """
    Get all configured social media platforms.

    Usage in template:
        {% load social_media %}
        {% get_social_media as social_media %}
        {% for platform, config in social_media.items %}
            <a href="{{ config.URL }}" target="_blank" rel="noopener noreferrer">
                <i class="{{ config.ICON }}"></i>
            </a>
        {% endfor %}

    Returns:
        Dictionary of social media platforms with URL and ICON
    """
    return getattr(settings, "SOCIAL_MEDIA", {})


@register.simple_tag
def get_social_media_url(platform: str) -> str:
    """
    Get the URL for a specific social media platform.

    Usage in template:
        {% load social_media %}
        {% get_social_media_url "facebook" as facebook_url %}
        {% if facebook_url %}
            <a href="{{ facebook_url }}">Visit our Facebook</a>
        {% endif %}

    Args:
        platform: The social media platform name (e.g., "facebook", "instagram")

    Returns:
        The URL string, or empty string if not configured
    """
    social_media = getattr(settings, "SOCIAL_MEDIA", {})
    return social_media.get(platform, {}).get("URL", "")


@register.simple_tag
def get_social_media_icon(platform: str) -> str:
    """
    Get the icon class for a specific social media platform.

    Usage in template:
        {% load social_media %}
        <i class="{% get_social_media_icon 'facebook' %}"></i>

    Args:
        platform: The social media platform name (e.g., "facebook", "instagram")

    Returns:
        The icon class string, or empty string if not configured
    """
    social_media = getattr(settings, "SOCIAL_MEDIA", {})
    return social_media.get(platform, {}).get("ICON", "")


@register.inclusion_tag("tawala/social_media_links.html")
def social_media_links(
    css_class: str = "", icon_size: str = "1.5rem"
) -> dict[str, str | dict[str, dict[str, str]]]:
    """
    Render social media links with icons.

    Usage in template:
        {% load social_media %}
        {% social_media_links css_class="d-flex gap-3" icon_size="2rem" %}

    Args:
        css_class: CSS classes to apply to the container
        icon_size: Size of the icons (CSS value)

    Returns:
        Context dictionary for the template
    """
    return {
        "social_media": getattr(settings, "SOCIAL_MEDIA", {}),
        "css_class": css_class,
        "icon_size": icon_size,
    }


@register.filter
def has_social_media(platform: str) -> bool:
    """
    Check if a social media platform is configured.

    Usage in template:
        {% load social_media %}
        {% if "facebook"|has_social_media %}
            <!-- Facebook is configured -->
        {% endif %}

    Args:
        platform: The social media platform name

    Returns:
        True if the platform is configured, False otherwise
    """
    social_media = getattr(settings, "SOCIAL_MEDIA", {})
    return platform in social_media
