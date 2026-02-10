from django.contrib import admin
from django.urls import include, path
from app.views import health_check


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check),
    path("api/", include("vault.urls")),
]
