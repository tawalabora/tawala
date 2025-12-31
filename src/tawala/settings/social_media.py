from enum import StrEnum
from typing import NotRequired, TypedDict

from .conf import Conf, ConfField


class SocialMediaConf(Conf):
    """Social Media configuration settings."""

    facebook = ConfField(env="SOCIAL_MEDIA_FACEBOOK", toml="social-media.facebook", type=str)
    twitter_x = ConfField(env="SOCIAL_MEDIA_TWITTER_X", toml="social-media.twitter-x", type=str)
    instagram = ConfField(env="SOCIAL_MEDIA_INSTAGRAM", toml="social-media.instagram", type=str)
    linkedin = ConfField(env="SOCIAL_MEDIA_LINKEDIN", toml="social-media.linkedin", type=str)
    whatsapp = ConfField(env="SOCIAL_MEDIA_WHATSAPP", toml="social-media.whatsapp", type=str)
    youtube = ConfField(env="SOCIAL_MEDIA_YOUTUBE", toml="social-media.youtube", type=str)


class Platform(StrEnum):
    FACEBOOK = "facebook"
    TWITTER_X = "twitter-x"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    WHATSAPP = "whatsapp"
    YOUTUBE = "youtube"


class PlatformConfig(TypedDict):
    """Configuration for a single social media platform."""

    URL: str
    ICON: str


class SocialMediaDict(TypedDict, total=False):
    """Type definition for social media configuration dictionary.

    All platforms are optional since they're only included if configured.
    """

    facebook: NotRequired[PlatformConfig]
    twitter_x: NotRequired[PlatformConfig]
    instagram: NotRequired[PlatformConfig]
    linkedin: NotRequired[PlatformConfig]
    whatsapp: NotRequired[PlatformConfig]
    youtube: NotRequired[PlatformConfig]


_social_media = SocialMediaConf()


def _get_social_media_config() -> SocialMediaDict:
    """Generate social media configuration dynamically."""
    config: SocialMediaDict = {}

    platforms = {
        Platform.FACEBOOK: _social_media.facebook,
        Platform.TWITTER_X: _social_media.twitter_x,
        Platform.INSTAGRAM: _social_media.instagram,
        Platform.LINKEDIN: _social_media.linkedin,
        Platform.WHATSAPP: _social_media.whatsapp,
        Platform.YOUTUBE: _social_media.youtube,
    }

    icons: dict[str, str] = {
        Platform.FACEBOOK: "bi bi-facebook",
        Platform.TWITTER_X: "bi bi-twitter-x",
        Platform.INSTAGRAM: "bi bi-instagram",
        Platform.LINKEDIN: "bi bi-linkedin",
        Platform.WHATSAPP: "bi bi-whatsapp",
        Platform.YOUTUBE: "bi bi-youtube",
    }

    # Build config for platforms that have URLs configured
    for platform, url in platforms.items():
        if url:  # Only include if URL is not None or empty string
            config[platform] = {  # type: ignore[literal-required]
                "URL": url,
                "ICON": icons.get(platform, "bi bi-link"),
            }

    return config


SOCIAL_MEDIA: SocialMediaDict = _get_social_media_config()
__all__ = ["SOCIAL_MEDIA"]
