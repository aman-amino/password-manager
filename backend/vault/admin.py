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


@admin.register(UserKeyMaterial)
class UserKeyMaterialAdmin(admin.ModelAdmin):
    list_display = ("user", "kdf_alg", "kdf_iterations", "created_at")
    search_fields = ("user__username", "user__email")


@admin.register(ScopeKey)
class ScopeKeyAdmin(admin.ModelAdmin):
    list_display = ("scope", "organization", "department", "key_version", "is_active", "created_at")
    list_filter = ("scope", "is_active", "organization")


@admin.register(VaultItem)
class VaultItemAdmin(admin.ModelAdmin):
    list_display = ("title", "scope", "owner", "organization", "is_deleted", "created_at")
    list_filter = ("scope", "is_deleted", "organization")
    search_fields = ("title", "owner__username")


@admin.register(VaultItemKey)
class VaultItemKeyAdmin(admin.ModelAdmin):
    list_display = ("vault_item", "recipient", "wrapped_key_alg", "created_at")
    search_fields = ("vault_item__title", "recipient__username")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "owner", "created_at")
    list_filter = ("kind",)
    search_fields = ("name", "owner__username")


@admin.register(VaultItemTag)
class VaultItemTagAdmin(admin.ModelAdmin):
    list_display = ("vault_item", "tag", "created_at")


@admin.register(AccessGrant)
class AccessGrantAdmin(admin.ModelAdmin):
    list_display = ("vault_item", "grantee", "granted_by", "is_active", "expires_at")
    list_filter = ("is_active",)


@admin.register(RecoveryKey)
class RecoveryKeyAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("action", "actor", "target_type", "target_id", "created_at")
    list_filter = ("action", "organization")
    search_fields = ("actor__username", "target_type", "target_id")
