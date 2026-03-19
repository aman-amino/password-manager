from django.contrib import admin
from .models import (
    AccessGrant,
    AuditEvent,
    RecoveryKey,
    ScopeKey,
    Tag,
    UserKeyMaterial,
    VaultItem,
    VaultItemKey,
    VaultItemTag,
)
from .utils import log_audit_event

class AuditLoggingMixin:
    """Mixin to log admin actions to the AuditEvent model."""
    def log_addition(self, request, obj, message):
        super().log_addition(request, obj, message)
        log_audit_event(
            request,
            action=AuditEvent.Action.CREATE,
            target_type=obj._meta.model_name,
            target_id=str(obj.pk),
            metadata={"admin_action": "addition", "message": message}
        )

    def log_change(self, request, obj, message):
        super().log_change(request, obj, message)
        log_audit_event(
            request,
            action=AuditEvent.Action.UPDATE,
            target_type=obj._meta.model_name,
            target_id=str(obj.pk),
            metadata={"admin_action": "change", "message": message}
        )

    def log_deletion(self, request, obj, object_repr):
        super().log_deletion(request, obj, object_repr)
        log_audit_event(
            request,
            action=AuditEvent.Action.DELETE,
            target_type=obj._meta.model_name,
            target_id=str(obj.pk),
            metadata={"admin_action": "deletion", "object_repr": object_repr}
        )

@admin.register(UserKeyMaterial)
class UserKeyMaterialAdmin(AuditLoggingMixin, admin.ModelAdmin):
    list_display = ("user", "kdf_alg", "kdf_iterations", "created_at")
    search_fields = ("user__username", "user__email")

@admin.register(ScopeKey)
class ScopeKeyAdmin(AuditLoggingMixin, admin.ModelAdmin):
    list_display = ("scope", "organization", "department", "key_version", "is_active", "created_at")
    list_filter = ("scope", "is_active", "organization")

@admin.register(VaultItem)
class VaultItemAdmin(AuditLoggingMixin, admin.ModelAdmin):
    list_display = ("title", "scope", "owner", "organization", "is_deleted", "created_at")
    list_filter = ("scope", "is_deleted", "organization")
    search_fields = ("title", "owner__username")

@admin.register(VaultItemKey)
class VaultItemKeyAdmin(AuditLoggingMixin, admin.ModelAdmin):
    list_display = ("vault_item", "recipient", "wrapped_key_alg", "created_at")
    search_fields = ("vault_item__title", "recipient__username")

@admin.register(Tag)
class TagAdmin(AuditLoggingMixin, admin.ModelAdmin):
    list_display = ("name", "kind", "owner", "created_at")
    list_filter = ("kind",)
    search_fields = ("name", "owner__username")

@admin.register(VaultItemTag)
class VaultItemTagAdmin(AuditLoggingMixin, admin.ModelAdmin):
    list_display = ("vault_item", "tag", "created_at")

@admin.register(AccessGrant)
class AccessGrantAdmin(AuditLoggingMixin, admin.ModelAdmin):
    list_display = ("vault_item", "grantee", "granted_by", "is_active", "expires_at")
    list_filter = ("is_active",)

@admin.register(RecoveryKey)
class RecoveryKeyAdmin(AuditLoggingMixin, admin.ModelAdmin):
    list_display = ("user", "created_at")

@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("action", "actor", "target_type", "target_id", "created_at")
    list_filter = ("action", "organization")
    search_fields = ("actor__username", "target_type", "target_id")
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False
