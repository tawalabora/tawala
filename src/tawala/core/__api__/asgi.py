"""
ASGI config

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/stable/howto/deployment/asgi/
"""

from os import environ

from django.core.asgi import get_asgi_application

from ...conf.preload import PKG

environ.setdefault("DJANGO_SETTINGS_MODULE", f"{PKG.name}.conf.settings")

application = get_asgi_application()
