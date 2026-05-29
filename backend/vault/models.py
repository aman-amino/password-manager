from django.conf import settings
from django.db import models
from django.utils import timezone

from app.models import Department, Organization


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserKeyMaterial(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="key_material")
    kdf_salt = models.BinaryField()
    kdf_iterations = models.PositiveIntegerField()
    kdf_alg = models.CharField(max_length=64, default="PBKDF2-HMAC-SHA-256")
    encrypted_user_key = models.BinaryField()

    def __str__(self) -> str:
        return f"KeyMaterial({self.user_id})"


class ScopeKey(TimeStampedModel):
    class Scope(models.TextChoices):
        ORG = "org", "Organization"
        DEPT = "dept", "Department"

    scope = models.CharField(max_length=10, choices=Scope.choices)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="scope_keys")
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.CASCADE, related_name="scope_keys")
    key_version = models.PositiveIntegerField(default=1)
    encrypted_scope_key = models.BinaryField()
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["scope", "organization", "department", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.scope}:{self.organization_id}:{self.department_id}:{self.key_version}"


class VaultItem(TimeStampedModel):
    class Scope(models.TextChoices):
        PERSONAL = "personal", "Personal"
        ORG = "org", "Organization"
        DEPT = "dept", "Department"

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vault_items")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="vault_items")
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL, related_name="vault_items")
    scope = models.CharField(max_length=10, choices=Scope.choices)
    title = models.CharField(max_length=200)
    item_type = models.CharField(max_length=50, default="generic")
    encrypted_blob = models.BinaryField()
    nonce = models.BinaryField()
    is_favorite = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def is_personal(self) -> bool:
        return self.scope == self.Scope.PERSONAL

    class Meta:
        indexes = [
            models.Index(fields=["organization", "scope", "is_deleted"]),
            models.Index(fields=["owner", "is_deleted"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.scope})"


class VaultItemKey(TimeStampedModel):
    vault_item = models.ForeignKey(VaultItem, on_delete=models.CASCADE, related_name="wrapped_keys")
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_keys")
    wrapped_key = models.BinaryField()
    wrapped_key_alg = models.CharField(max_length=64, default="ECDH-P256+A256GCM")

    class Meta:
        unique_together = ("vault_item", "recipient")


class Tag(TimeStampedModel):
    class Kind(models.TextChoices):
        SYSTEM = "system", "System"
        PERSONAL = "personal", "Personal"

    name = models.CharField(max_length=100)
    kind = models.CharField(max_length=20, choices=Kind.choices)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name="tags")

    class Meta:
        unique_together = ("name", "kind", "owner")

    def __str__(self) -> str:
        return self.name


class VaultItemTag(TimeStampedModel):
    vault_item = models.ForeignKey(VaultItem, on_delete=models.CASCADE, related_name="tag_links")
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name="vault_links")

    class Meta:
        unique_together = ("vault_item", "tag")


class AccessGrant(TimeStampedModel):
    vault_item = models.ForeignKey(VaultItem, on_delete=models.CASCADE, related_name="access_grants")
    grantee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="access_grants")
    granted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="grants_given")
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("vault_item", "grantee")

    def is_valid(self) -> bool:
        if not self.is_active:
            return False
        if self.expires_at is None:
            return True
        return self.expires_at > timezone.now()


class RecoveryKey(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recovery_key")
    public_key = models.BinaryField()
    wrapped_recovery_key = models.BinaryField()

    def __str__(self) -> str:
        return f"RecoveryKey({self.user_id})"


class AuditEvent(TimeStampedModel):
    class Action(models.TextChoices):
        READ = "read", "Read"
        CREATE = "create", "Create"
        UPDATE = "update", "Update"
        DELETE = "delete", "Delete"
        LOGIN = "login", "Login"
        ADMIN = "admin", "Admin"

    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="audit_events")
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL, related_name="audit_events")
    target_type = models.CharField(max_length=50)
    target_id = models.CharField(max_length=64)
    action = models.CharField(max_length=20, choices=Action.choices)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization", "created_at"]),
            models.Index(fields=["actor", "created_at"]),
            models.Index(fields=["target_type", "target_id"]),
        ]
