from dataclasses import dataclass
from typing import Iterable

from django.db.models import Q

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
        return PolicyDecision(False, "personal-owner-only")
    if item.owner_id == user.id:
        return PolicyDecision(True, "owner")
    if user.role == User.Role.SUPERADMIN:
        return PolicyDecision(True, "superadmin")
    if user.role == User.Role.ADMIN and item.organization_id == user.organization_id:
        return PolicyDecision(True, "admin-org")
    if user.role == User.Role.SUBADMIN and item.department_id == user.department_id:
        return PolicyDecision(True, "subadmin-dept")
    if AccessGrant.objects.filter(vault_item=item, grantee=user, is_active=True).exists():
        return PolicyDecision(True, "access-grant")
    return PolicyDecision(False, "no-access")


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
        return PolicyDecision(True, "subadmin-dept")
    return PolicyDecision(False, "no-access")


def vault_item_queryset_for_user(user: User):
    if not user.is_authenticated:
        return VaultItem.objects.none()
    base = VaultItem.objects.filter(is_deleted=False, organization=user.organization).exclude(
        Q(scope=VaultItem.Scope.PERSONAL) & ~Q(owner=user)
    )
    if user.role == User.Role.SUPERADMIN:
        return base
    if user.role == User.Role.ADMIN:
        return base
    if user.role == User.Role.SUBADMIN:
        return base.filter(Q(department=user.department) | Q(owner=user))
    # regular user
    grant_ids = AccessGrant.objects.filter(grantee=user, is_active=True).values_list("vault_item_id", flat=True)
    return base.filter(Q(owner=user) | Q(id__in=grant_ids))


def filter_personal_owner_only(items: Iterable[VaultItem], user: User) -> Iterable[VaultItem]:
    for item in items:
        if item.is_personal() and item.owner_id != user.id:
            continue
        yield item
