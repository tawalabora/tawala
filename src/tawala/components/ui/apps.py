from django.apps import AppConfig

from ...core import PKG


class UIConfig(AppConfig):
    name = f"{PKG.name}.components.ui"
