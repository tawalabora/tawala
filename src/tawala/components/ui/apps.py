from django.apps import AppConfig
from tawala.core.conf.pre import PKG


class UIConfig(AppConfig):
    name = f"{PKG.name}.components.ui"
