from rest_framework.permissions import BasePermission

from .policy import can_view_vault_item


class CanViewVaultItem(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        return can_view_vault_item(request.user, obj).allowed
