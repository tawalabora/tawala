from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from tawala.management.utils.constants import TAWALA

if TYPE_CHECKING:
    from tawala.management.settings.base import OrgConf

_ORG: "OrgConf" = settings.ORG
_ORG_NAME = _ORG.name or TAWALA.capitalize()

admin.site.site_header = _(f"{_ORG_NAME} Admin")
admin.site.site_title = _(f"{_ORG_NAME} Admin Portal")
admin.site.index_title = _(f"Welcome to {_ORG_NAME} Admin")
