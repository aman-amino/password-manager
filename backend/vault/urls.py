from rest_framework.routers import DefaultRouter

from .views import VaultItemViewSet

router = DefaultRouter()
router.register(r"vault-items", VaultItemViewSet, basename="vault-item")

urlpatterns = router.urls
