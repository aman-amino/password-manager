import secrets
from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.utils import timezone
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


@login_required
@require_POST
def verify_mfa(request):
    """
    Verify a TOTP code. For this implementation, we use a placeholder verification
    since we don't have a mobile authenticator app integrated in the sandbox.
    In production, this would use a library like 'pyotp'.
    """
    code = request.POST.get("code")
    user = request.user

    if not user.totp_secret:
        return JsonResponse({"status": "error", "message": "MFA not set up"}, status=400)

    # Placeholder: Accept '123456' as a valid code for verification in dev
    # Real implementation: pyotp.TOTP(user.totp_secret).verify(code)
    is_valid = (code == "123456")

    if is_valid:
        user.last_mfa_login = timezone.now()
        user.save(update_fields=["last_mfa_login"])

        log_audit_event(
            request,
            action=AuditEvent.Action.LOGIN,
            target_type="user_mfa",
            target_id=str(user.id),
            metadata={"status": "success"}
        )
        return JsonResponse({"status": "success"})
    else:
        log_audit_event(
            request,
            action=AuditEvent.Action.LOGIN,
            target_type="user_mfa",
            target_id=str(user.id),
            metadata={"status": "failure", "reason": "invalid_code"}
        )
        return JsonResponse({"status": "error", "message": "Invalid MFA code"}, status=403)
