# ==============================================================================
# Authentication & Password validation
# https://docs.djangoproject.com/en/stable/ref/settings/#auth-password-validators
# ==============================================================================
from typing import Literal

AUTH_PASSWORD_VALIDATORS: list[dict[Literal["NAME"], str]] = [
    {"NAME": f"django.contrib.auth.password_validation.{validator}"}
    for validator in [
        "UserAttributeSimilarityValidator",
        "MinimumLengthValidator",
        "CommonPasswordValidator",
        "NumericPasswordValidator",
    ]
]


__all__ = ["AUTH_PASSWORD_VALIDATORS"]
