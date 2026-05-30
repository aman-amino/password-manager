from dataclasses import dataclass
from typing import Iterable
from django.utils import timezone
from django.db.models import Q, OuterRef, Exists

from app.models import User
from .models import AccessGrant, VaultItem


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str


def can_view_vault_item(user: User, item: VaultItem) -> PolicyDecision:
    if not user.is_authenticated:
        return PolicyDecision(False, "unauthenticated")
    if item.is_deleted:
        return PolicyDecision(False, "deleted")
    if item.is_personal() and item.owner_id != user.id:
        # Check for active and unexpired access grants BEFORE denying personal access to non-owners
        now = timezone.now()
        if AccessGrant.objects.filter(
            vault_item=item,
            grantee=user,
            is_active=True
        ).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=now)
        ).exists():
            return PolicyDecision(True, "access-grant")
        return PolicyDecision(False, "personal-owner-only")

    if item.owner_id == user.id:
        return PolicyDecision(True, "owner")
    if user.role == User.Role.SUPERADMIN:
        return PolicyDecision(True, "superadmin")
    if user.role == User.Role.ADMIN and item.organization_id == user.organization_id:
        return PolicyDecision(True, "admin-org")
    if user.role == User.Role.SUBADMIN and item.department_id == user.department_id:
        # Subadmins can only see non-personal items in their department if the scope is DEPT
        # (Owners and those with grants are already handled above)
        if item.scope == VaultItem.Scope.DEPT:
            return PolicyDecision(True, "subadmin-dept")

    # General grant check for non-personal items
    now = timezone.now()
    if AccessGrant.objects.filter(
        vault_item=item,
        grantee=user,
        is_active=True
    ).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=now)
    ).exists():
        return PolicyDecision(True, "access-grant")

    return PolicyDecision(False, "no-access")


def can_create_vault_item(user: User, scope: str) -> PolicyDecision:
    if not user.is_authenticated:
        return PolicyDecision(False, "unauthenticated")

    if scope == VaultItem.Scope.PERSONAL:
        return PolicyDecision(True, "allowed")

    if scope == VaultItem.Scope.DEPT:
        if user.role in (User.Role.SUPERADMIN, User.Role.ADMIN, User.Role.SUBADMIN):
            return PolicyDecision(True, "allowed")
        return PolicyDecision(False, "insufficient-role-for-dept-scope")

    if scope == VaultItem.Scope.ORG:
        if user.role in (User.Role.SUPERADMIN, User.Role.ADMIN):
            return PolicyDecision(True, "allowed")
        return PolicyDecision(False, "insufficient-role-for-org-scope")

    return PolicyDecision(False, "invalid-scope")


def can_manage_vault_item(user: User, item: VaultItem) -> PolicyDecision:
    if not user.is_authenticated:
        return PolicyDecision(False, "unauthenticated")
    if item.is_personal() and item.owner_id != user.id:
        return PolicyDecision(False, "personal-owner-only")
    if item.owner_id == user.id:
        return PolicyDecision(True, "owner")
    if user.role in (User.Role.SUPERADMIN, User.Role.ADMIN) and item.organization_id == user.organization_id:
        return PolicyDecision(True, "org-admin")
    if user.role == User.Role.SUBADMIN and item.department_id == user.department_id:
        # Subadmins can only manage non-personal items in their department if the scope is DEPT
        if item.scope == VaultItem.Scope.DEPT:
            return PolicyDecision(True, "subadmin-dept")
    return PolicyDecision(False, "no-access")


def vault_item_queryset_for_user(user: User):
    if not user.is_authenticated:
        return VaultItem.objects.none()

    if user.role == User.Role.SUPERADMIN:
        # Superadmins see everything except other people's personal items
        return VaultItem.objects.filter(is_deleted=False).exclude(
            Q(scope=VaultItem.Scope.PERSONAL) & ~Q(owner=user)
        )

    # regular user + others
    now = timezone.now()

    # Optimization: Use Exists subquery instead of evaluating a list of IDs
    active_grants = AccessGrant.objects.filter(
        vault_item=OuterRef('pk'),
        grantee=user,
        is_active=True
    ).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=now)
    )

    base = VaultItem.objects.filter(is_deleted=False, organization=user.organization)

    if user.role == User.Role.ADMIN:
        # Admins see everything in org except other's personal items, PLUS grants
        return base.exclude(
            Q(scope=VaultItem.Scope.PERSONAL) & ~Q(owner=user) & ~Exists(active_grants)
        )

    if user.role == User.Role.SUBADMIN:
        # Subadmins see items they own, items with grants, and DEPT items in their department
        return base.filter(
            Q(owner=user) |
            Exists(active_grants) |
            (Q(department=user.department) & Q(scope=VaultItem.Scope.DEPT))
        )

    # regular user
    return base.filter(Q(owner=user) | Exists(active_grants))


def filter_personal_owner_only(items: Iterable[VaultItem], user: User) -> Iterable[VaultItem]:
    for item in items:
        if item.is_personal() and item.owner_id != user.id:
            continue
        yield item
