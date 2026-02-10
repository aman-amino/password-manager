from django.conf import settings
from django.db import models

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
