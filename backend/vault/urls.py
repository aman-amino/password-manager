from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VaultItemViewSet, AuditEventViewSet, AccessGrantViewSet
from .auth_views import RegisterView, LoginParamsView, LoginView, LogoutView, MeView, UserViewSet

router = DefaultRouter()
router.register(r"vault-items", VaultItemViewSet, basename="vault-item")
router.register(r"audit-events", AuditEventViewSet, basename="audit-event")
router.register(r"access-grants", AccessGrantViewSet, basename="access-grant")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login-params/", LoginParamsView.as_view(), name="login-params"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    path("users/", UserViewSet.as_view(), name="users"),
    path("", include(router.urls)),
]
