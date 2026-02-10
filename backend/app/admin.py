from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Department, Organization, User


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    search_fields = ("name", "slug")
    list_filter = ("is_active",)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "slug", "is_active", "created_at")
    search_fields = ("name", "slug", "organization__name")
    list_filter = ("organization", "is_active")


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Security", {"fields": ("role", "organization", "department", "mfa_enabled")}),
    )
    list_display = DjangoUserAdmin.list_display + ("role", "organization", "department", "mfa_enabled")
    list_filter = DjangoUserAdmin.list_filter + ("role", "organization", "department", "mfa_enabled")
