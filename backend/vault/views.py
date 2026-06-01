from django.db.models import Q
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from app.models import User
from .models import AuditEvent, VaultItem, AccessGrant
from .permissions import CanViewVaultItem, CanManageVaultItem, CanCreateVaultItem, RequiresMFA
from .policy import can_manage_vault_item, vault_item_queryset_for_user
from .serializers import VaultItemSerializer, AuditEventSerializer, AccessGrantSerializer
from .utils import log_audit_event


class VaultItemViewSet(viewsets.ModelViewSet):
    serializer_class = VaultItemSerializer
    permission_classes = [IsAuthenticated, RequiresMFA, CanViewVaultItem, CanCreateVaultItem]

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), RequiresMFA(), CanCreateVaultItem()]
        if self.action in ("update", "partial_update", "destroy"):
            return [IsAuthenticated(), RequiresMFA(), CanManageVaultItem(), CanCreateVaultItem()]
        return super().get_permissions()

    def get_queryset(self):
        # Optimization: Only select 'owner' as 'organization' and 'department' are rendered as IDs in the serializer
        return vault_item_queryset_for_user(self.request.user).select_related("owner")

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

class AuditEventViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, RequiresMFA]
    serializer_class = AuditEventSerializer

    def get_queryset(self):
        user = self.request.user
        target_id = self.request.query_params.get('target_id')
        target_type = self.request.query_params.get('target_type')

        qs = AuditEvent.objects.select_related("actor", "organization").all()
        if target_id:
            qs = qs.filter(target_id=target_id)
        if target_type:
            qs = qs.filter(target_type=target_type)

        if user.role == User.Role.SUPERADMIN:
            return qs.order_by("-created_at")
        if user.role in (User.Role.ADMIN, User.Role.SUBADMIN) and user.organization:
            return qs.filter(organization=user.organization).order_by("-created_at")
        return qs.filter(actor=user).order_by("-created_at")

class AccessGrantViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, RequiresMFA]
    serializer_class = AccessGrantSerializer

    def get_queryset(self):
        user = self.request.user
        # Use select_related to optimize retrieval of related fields and avoid N+1 queries during serialization.
        return (
            AccessGrant.objects.filter(grantee=user, is_active=True)
            | AccessGrant.objects.filter(granted_by=user)
        ).select_related("grantee", "vault_item", "granted_by")

    def perform_create(self, serializer):
        instance = serializer.save()
        log_audit_event(self.request, AuditEvent.Action.UPDATE, "access_grant", instance.id, metadata={"grantee": instance.grantee.username})
