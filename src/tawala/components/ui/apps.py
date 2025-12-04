from django.apps import AppConfig

from ...conf.preload import PKG


class UIConfig(AppConfig):
    name = f"{PKG.name}.components.ui"
