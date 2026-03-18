from dataclasses import dataclass
from typing import Iterable
from django.utils import timezone
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

    if user.role == User.Role.SUPERADMIN:
        # Superadmins see everything except other people's personal items
        return VaultItem.objects.filter(is_deleted=False).exclude(
            Q(scope=VaultItem.Scope.PERSONAL) & ~Q(owner=user)
        )

    # regular user + others
    now = timezone.now()
    grant_ids = AccessGrant.objects.filter(
        grantee=user,
        is_active=True
    ).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=now)
    ).values_list("vault_item_id", flat=True)

    base = VaultItem.objects.filter(is_deleted=False, organization=user.organization)

    if user.role == User.Role.ADMIN:
        # Admins see everything in org except other's personal items, PLUS grants
        return base.exclude(
            Q(scope=VaultItem.Scope.PERSONAL) & ~Q(owner=user) & ~Q(id__in=grant_ids)
        )

    if user.role == User.Role.SUBADMIN:
        return base.filter(
            Q(department=user.department) | Q(owner=user) | Q(id__in=grant_ids)
        ).exclude(
            Q(scope=VaultItem.Scope.PERSONAL) & ~Q(owner=user) & ~Q(id__in=grant_ids)
        )

    # regular user
    return base.filter(Q(owner=user) | Q(id__in=grant_ids))


def filter_personal_owner_only(items: Iterable[VaultItem], user: User) -> Iterable[VaultItem]:
    for item in items:
        if item.is_personal() and item.owner_id != user.id:
            continue
        yield item
