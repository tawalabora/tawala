from django.apps import AppConfig

from ..core.conf.pre import PKG


class UIConfig(AppConfig):
    name = f"{PKG.name}.ui"
