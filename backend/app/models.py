from django.contrib.auth.models import AbstractUser
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Organization(TimeStampedModel):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class Department(TimeStampedModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="departments")
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("organization", "slug")

    def __str__(self) -> str:
        return f"{self.organization.name} / {self.name}"


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPERADMIN = "superadmin", "Superadmin"
        ADMIN = "admin", "Admin"
        SUBADMIN = "subadmin", "Subadmin"
        USER = "user", "User"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL, related_name="users")
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL, related_name="users")
    mfa_enabled = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.username
