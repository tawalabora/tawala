from django.utils.csp import CSP  # type: ignore[reportMissingTypeStubs]

from .auth import *  # noqa: F403
from .base import *  # noqa: F403
from .contactinfo import *  # noqa: F403
from .databases import *  # noqa: F403
from .generate import *  # noqa: F403
from .runcommands import *  # noqa: F403
from .security import *  # noqa: F403
from .social import *  # noqa: F403
from .storages import *  # noqa: F403
from .tailwind import *  # noqa: F403
from .urls import *  # noqa: F403

# ==============================================================================
# Internationalization
# https://docs.djangoproject.com/en/stable/topics/i18n/
# ==============================================================================

LANGUAGE_CODE: str = "en-us"

TIME_ZONE: str = "Africa/Nairobi"

USE_I18N: bool = True

USE_TZ: bool = True


# ==============================================================================
# Content Security Policy (CSP)
# https://docs.djangoproject.com/en/stable/howto/csp/
# ==============================================================================

SECURE_CSP: dict[str, list[str]] = {
    "default-src": [CSP.SELF],
    "script-src": [CSP.SELF, CSP.NONCE],
    "style-src": [
        CSP.SELF,
        CSP.NONCE,
        "https://fonts.googleapis.com",  # Google Fonts CSS
    ],
    "font-src": [
        CSP.SELF,
        "https://fonts.gstatic.com",  # Google Fonts font files
    ],
}
