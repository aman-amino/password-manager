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
