from rest_framework.permissions import BasePermission
from app.models import User
from .models import VaultItem
from .policy import can_view_vault_item, can_manage_vault_item


class CanCreateVaultItem(BasePermission):
    def has_permission(self, request, view) -> bool:
        if request.method != "POST":
            return True

        user = request.user
        if not user or not user.is_authenticated:
            return False

        scope = request.data.get("scope")
        if scope == VaultItem.Scope.ORG:
            return user.role in (User.Role.SUPERADMIN, User.Role.ADMIN)
        if scope == VaultItem.Scope.DEPT:
            return user.role in (User.Role.SUPERADMIN, User.Role.ADMIN, User.Role.SUBADMIN)

        return True


class CanViewVaultItem(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        return can_view_vault_item(request.user, obj).allowed


class CanManageVaultItem(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        return can_manage_vault_item(request.user, obj).allowed


class CanCreateVaultItem(BasePermission):
    """
    Enforces RBAC for vault item creation.
    PERSONAL: Any authenticated user.
    ORG: Superadmin or Admin only.
    DEPT: Superadmin, Admin, or Subadmin only.
    """
    def has_permission(self, request, view) -> bool:
        if request.method != "POST":
            return True

        user = request.user
        if not user or not user.is_authenticated:
            return False

        scope = request.data.get("scope")
        # Defense in Depth: PERSONAL items are unrestricted for authenticated users
        if scope == VaultItem.Scope.PERSONAL:
            return True

        # ORG-scoped items require administrative privileges within the organization
        if scope == VaultItem.Scope.ORG:
            return user.role in (User.Role.SUPERADMIN, User.Role.ADMIN)

        # DEPT-scoped items allow Subadmins to manage department-level secrets
        if scope == VaultItem.Scope.DEPT:
            return user.role in (User.Role.SUPERADMIN, User.Role.ADMIN, User.Role.SUBADMIN)

        return False
