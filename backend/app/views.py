import secrets
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from .models import AdminConfig, User
from vault.utils import log_audit_event
from vault.models import AuditEvent


def is_superadmin(user):
    return user.is_authenticated and (user.role == User.Role.SUPERADMIN or user.is_superuser)


def home(request):
    return render(request, "app/index.html")


def status(request):
    return JsonResponse({"status": "ok", "endpoints": ["/health/", "/api/vault-items/"]})


def health_check(request):
    return JsonResponse({"status": "ok"})


@require_POST
@user_passes_test(is_superadmin)
def rotate_admin_url(request):
    # Deactivate old tokens
    AdminConfig.objects.all().update(is_active=False)
    # Create new token
    new_token = secrets.token_urlsafe(32)
    config = AdminConfig.objects.create(admin_token=new_token)

    log_audit_event(
        request,
        action=AuditEvent.Action.ADMIN,
        target_type="admin_config",
        target_id=str(config.id),
        metadata={"action": "rotate_admin_url"}
    )

    admin_url = f"/admin_{new_token}/"
    return JsonResponse({"admin_url": admin_url})
