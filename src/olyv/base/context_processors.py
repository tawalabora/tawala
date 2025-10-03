from django.conf import settings


def site(request):
    return {
        "SITE_NAME": getattr(settings, "SITE_NAME", ""),
        "SITE_DESCRIPTION": getattr(settings, "SITE_DESCRIPTION", ""),
        "SITE_URL": getattr(settings, "SITE_URL", ""),
        "SITE_LOGO": getattr(settings, "SITE_LOGO", ""),
        "SITE_KEYWORDS": getattr(settings, "SITE_KEYWORDS", ""),
        "SITE_HERO_1": getattr(settings, "SITE_HERO_1", ""),
        "SITE_FAVICON": getattr(settings, "SITE_FAVICON", ""),
        "SITE_APPLE_TOUCH_ICON": getattr(settings, "SITE_APPLE_TOUCH_ICON", ""),
        "SITE_ANDROID_CHROME_ICON": getattr(settings, "SITE_ANDROID_CHROME_ICON", ""),
        "SITE_MSTILE": getattr(settings, "SITE_MSTILE", ""),
        "SITE_MANIFEST": getattr(settings, "SITE_MANIFEST", ""),
    }
