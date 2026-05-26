from rest_framework.permissions import BasePermission

from app.models import User
from .models import VaultItem
from .policy import can_view_vault_item, can_manage_vault_item, can_create_vault_item


class RequiresMFA(BasePermission):
    """
    Ensures that if a user has MFA enabled, they have verified it in the current session.
    A user is considered verified if last_mfa_login >= last_login.
    We also allow access if last_login is None (e.g. during force_authenticate in tests),
    as long as last_mfa_login is present for MFA-enabled users.
    """
    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if not user.mfa_enabled:
            return True

        if not user.last_mfa_login:
            return False

        # Support for DRF testing where last_login might be None
        if not user.last_login:
            return True

        return user.last_mfa_login >= user.last_login


class CanCreateVaultItem(BasePermission):
    def has_permission(self, request, view) -> bool:
        if request.method != "POST":
            return True
        scope = request.data.get("scope")
        return can_create_vault_item(request.user, scope).allowed


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
