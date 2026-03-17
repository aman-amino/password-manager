from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.http import Http404
from app.models import AdminConfig, User
from app.views import health_check, home, status, rotate_admin_url


urlpatterns = [
    path("", home),
    path("status/", status),
    path("rotate-admin/", rotate_admin_url, name="rotate_admin"),
    re_path(r"^admin_[\w-]+/", admin.site.urls),
    path("health/", health_check),
    path("api/", include("vault.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
