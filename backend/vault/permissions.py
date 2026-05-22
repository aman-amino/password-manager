from rest_framework.permissions import BasePermission

from .policy import can_view_vault_item, can_manage_vault_item, can_create_vault_item


class CanCreateVaultItem(BasePermission):
    def has_permission(self, request, view) -> bool:
        if request.method != "POST":
            return True
        scope = request.data.get("scope")
        return can_create_vault_item(request.user, scope).allowed


class CanViewVaultItem(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        return can_view_vault_item(request.user, obj).allowed


class CanManageVaultItem(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        return can_manage_vault_item(request.user, obj).allowed
