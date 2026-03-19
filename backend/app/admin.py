from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import Department, Organization, User
from vault.utils import log_audit_event
from vault.models import AuditEvent

class AuditLoggingMixin:
    """Mixin to log admin actions to the AuditEvent model."""
    def log_addition(self, request, obj, message):
        super().log_addition(request, obj, message)
        log_audit_event(
            request,
            action=AuditEvent.Action.CREATE,
            target_type=obj._meta.model_name,
            target_id=str(obj.pk),
            metadata={"admin_action": "addition", "message": message}
        )

    def log_change(self, request, obj, message):
        super().log_change(request, obj, message)
        log_audit_event(
            request,
            action=AuditEvent.Action.UPDATE,
            target_type=obj._meta.model_name,
            target_id=str(obj.pk),
            metadata={"admin_action": "change", "message": message}
        )

    def log_deletion(self, request, obj, object_repr):
        super().log_deletion(request, obj, object_repr)
        log_audit_event(
            request,
            action=AuditEvent.Action.DELETE,
            target_type=obj._meta.model_name,
            target_id=str(obj.pk),
            metadata={"admin_action": "deletion", "object_repr": object_repr}
        )

@admin.register(Organization)
class OrganizationAdmin(AuditLoggingMixin, admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    search_fields = ("name", "slug")
    list_filter = ("is_active",)

@admin.register(Department)
class DepartmentAdmin(AuditLoggingMixin, admin.ModelAdmin):
    list_display = ("name", "organization", "slug", "is_active", "created_at")
    search_fields = ("name", "slug", "organization__name")
    list_filter = ("organization", "is_active")

@admin.register(User)
class UserAdmin(AuditLoggingMixin, DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Security", {"fields": ("role", "organization", "department", "mfa_enabled")}),
    )
    list_display = DjangoUserAdmin.list_display + ("role", "organization", "department", "mfa_enabled")
    list_filter = DjangoUserAdmin.list_filter + ("role", "organization", "department", "mfa_enabled")
