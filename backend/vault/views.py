from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from .models import VaultItem
from .permissions import CanViewVaultItem
from .policy import can_manage_vault_item, vault_item_queryset_for_user
from .serializers import VaultItemSerializer


class VaultItemViewSet(viewsets.ModelViewSet):
    serializer_class = VaultItemSerializer
    permission_classes = [IsAuthenticated, CanViewVaultItem]

    def get_queryset(self):
        return vault_item_queryset_for_user(self.request.user)

    def perform_update(self, serializer):
        decision = can_manage_vault_item(self.request.user, serializer.instance)
        if not decision.allowed:
            raise PermissionDenied(decision.reason)
        serializer.save()

    def perform_destroy(self, instance):
        decision = can_manage_vault_item(self.request.user, instance)
        if not decision.allowed:
            raise PermissionDenied(decision.reason)
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])
