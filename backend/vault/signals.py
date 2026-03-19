from django.contrib.auth.signals import user_logged_in, user_logged_out
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
        metadata={"username": user.username, "event": "login"}
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if user:
        log_audit_event(
            request,
            action=AuditEvent.Action.LOGIN,
            target_type="user",
            target_id=str(user.id),
            metadata={"username": user.username, "event": "logout"}
        )
