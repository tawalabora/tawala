from django.conf import settings
from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path

urlpatterns: list[URLPattern | URLResolver] = [
    path(settings.BROWSER_RELOAD_URL, include("django_browser_reload.urls")),
    path(settings.ADMIN_URL, admin.site.urls),
    *(
        [path("", include(f"{settings.MAIN_INSTALLED_APP}.urls"))]
        if settings.MAIN_INSTALLED_APP
        else []
    ),
]
