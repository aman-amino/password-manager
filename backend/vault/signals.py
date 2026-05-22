from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import AuditEvent
from .utils import log_audit_event

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    log_audit_event(
        request,
        action=AuditEvent.Action.LOGIN,
        target_type="user",
        target_id=str(user.id),
        metadata={"username": user.username}
    )

from django.contrib.auth.signals import user_logged_out, user_login_failed

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if user:
        log_audit_event(
            request,
            action=AuditEvent.Action.LOGIN,
            target_type="user_logout",
            target_id=str(user.id),
            metadata={"username": user.username}
        )

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    log_audit_event(
        request,
        action=AuditEvent.Action.LOGIN,
        target_type="user_login_failure",
        target_id="0",
        metadata={"username": credentials.get("username", "unknown")}
    )
