from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from app.views import health_check, home


urlpatterns = [
    path("", home),
    path("admin/", admin.site.urls),
    path("health/", health_check),
    path("api/", include("vault.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
