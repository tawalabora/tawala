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
    return settings.SOCIAL_MEDIA


@register.inclusion_tag(f"{settings.PKG['name']}/social_media_links.html")
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
        "social_media": settings.SOCIAL_MEDIA,
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
    return platform in settings.SOCIAL_MEDIA


@register.simple_tag
def get_facebook_url() -> str:
    """Returns the Facebook URL."""
    return settings.SOCIAL_MEDIA["facebook"]["URL"]


@register.simple_tag
def get_twitter_x_url() -> str:
    """Returns the Twitter/X URL."""
    return settings.SOCIAL_MEDIA["twitter-x"]["URL"]


@register.simple_tag
def get_instagram_url() -> str:
    """Returns the Instagram URL."""
    return settings.SOCIAL_MEDIA["instagram"]["URL"]


@register.simple_tag
def get_linkedin_url() -> str:
    """Returns the LinkedIn URL."""
    return settings.SOCIAL_MEDIA["linkedin"]["URL"]


@register.simple_tag
def get_whatsapp_url() -> str:
    """Returns the WhatsApp URL."""
    return settings.SOCIAL_MEDIA["whatsapp"]["URL"]


@register.simple_tag
def get_youtube_url() -> str:
    """Returns the YouTube URL."""
    return settings.SOCIAL_MEDIA["youtube"]["URL"]


# Specific getters for each platform - Icon
@register.simple_tag
def get_facebook_icon() -> str:
    """Returns the Facebook icon class."""
    return settings.SOCIAL_MEDIA["facebook"]["ICON"]


@register.simple_tag
def get_twitter_x_icon() -> str:
    """Returns the Twitter/X icon class."""
    return settings.SOCIAL_MEDIA["twitter-x"]["ICON"]


@register.simple_tag
def get_instagram_icon() -> str:
    """Returns the Instagram icon class."""
    return settings.SOCIAL_MEDIA["instagram"]["ICON"]


@register.simple_tag
def get_linkedin_icon() -> str:
    """Returns the LinkedIn icon class."""
    return settings.SOCIAL_MEDIA["linkedin"]["ICON"]


@register.simple_tag
def get_whatsapp_icon() -> str:
    """Returns the WhatsApp icon class."""
    return settings.SOCIAL_MEDIA["whatsapp"]["ICON"]


@register.simple_tag
def get_youtube_icon() -> str:
    """Returns the YouTube icon class."""
    return settings.SOCIAL_MEDIA["youtube"]["ICON"]
