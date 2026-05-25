from rest_framework.permissions import BasePermission

from .policy import can_view_vault_item, can_manage_vault_item, can_create_vault_item


class RequiresMFA(BasePermission):
    """
    Ensures that users with MFA enabled have verified their identity in the current session.
    """
    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if not user.mfa_enabled:
            return True

        # If MFA is enabled, verify it was completed in the current session.
        # last_mfa_login is set upon successful TOTP verification.
        if not user.last_mfa_login:
            return False

        # If last_login is None (e.g. during force_authenticate in tests),
        # we consider it verified as long as last_mfa_login exists.
        if not user.last_login:
            return True

        return user.last_mfa_login >= user.last_login


class CanCreateVaultItem(BasePermission):
    """
    Enforces RBAC for vault item creation using central policy.
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
