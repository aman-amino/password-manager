from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from .models import AuditEvent, VaultItem
from .permissions import CanViewVaultItem, CanManageVaultItem
from .policy import can_manage_vault_item, vault_item_queryset_for_user
from .serializers import VaultItemSerializer
from .utils import log_audit_event


class VaultItemViewSet(viewsets.ModelViewSet):
    serializer_class = VaultItemSerializer
    permission_classes = [IsAuthenticated, CanViewVaultItem]

    def get_permissions(self):
        if self.action in ("update", "partial_update", "destroy"):
            return [IsAuthenticated(), CanManageVaultItem()]
        return super().get_permissions()

    def get_queryset(self):
        return vault_item_queryset_for_user(self.request.user)

    def list(self, request, *args, **kwargs):
        log_audit_event(request, AuditEvent.Action.READ, "vault_item_list", "bulk")
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        log_audit_event(request, AuditEvent.Action.READ, "vault_item", instance.id)
        return super().retrieve(request, *args, **kwargs)

    def perform_create(self, serializer):
        instance = serializer.save()
        log_audit_event(self.request, AuditEvent.Action.CREATE, "vault_item", instance.id)

    def perform_update(self, serializer):
        instance = serializer.save()
        log_audit_event(self.request, AuditEvent.Action.UPDATE, "vault_item", instance.id)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])
        log_audit_event(self.request, AuditEvent.Action.DELETE, "vault_item", instance.id)
