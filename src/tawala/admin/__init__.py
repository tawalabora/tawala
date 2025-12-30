from django.conf import settings
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

site_name = settings.SITE["name"]
admin.site.site_header = _(f"{site_name} Admin")
admin.site.site_title = _(f"{site_name} Admin Portal")
admin.site.index_title = _(f"Welcome to {site_name} Admin")
