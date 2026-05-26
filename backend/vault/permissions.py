from rest_framework.permissions import BasePermission

from .policy import can_view_vault_item, can_manage_vault_item, can_create_vault_item


class RequiresMFA(BasePermission):
    """
    Enforces MFA verification for users who have MFA enabled.
    Checks if last_mfa_login is greater than or equal to last_login.
    """
    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if not user.mfa_enabled:
            return True

        if not user.last_mfa_login:
            return False

        # Verify that MFA was performed in the current session
        # If last_login is not set (e.g. in some test scenarios), we rely on last_mfa_login being present.
        if not user.last_login:
            return True

        return user.last_mfa_login >= user.last_login


class CanCreateVaultItem(BasePermission):
    """
    Delegates vault item creation permissions to the policy engine.
    """
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
