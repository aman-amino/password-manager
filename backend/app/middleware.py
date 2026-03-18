import re
from django.http import Http404
from .models import AdminConfig, User
from vault.utils import log_audit_event
from vault.models import AuditEvent

class AdminTokenMiddleware:
    # Match path segments that strictly look like /admin_<token>/
    ADMIN_PATH_RE = re.compile(r'^/admin_([\w-]+)/')

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        match = self.ADMIN_PATH_RE.match(path)

        if match:
            token = match.group(1)
            # Bypass check ONLY if NO active tokens exist yet (initial setup)
            if not AdminConfig.objects.filter(is_active=True).exists():
                # Still log that we are in initial setup mode
                log_audit_event(
                    request,
                    action=AuditEvent.Action.ADMIN,
                    target_type="admin_setup",
                    target_id="initial_bypass",
                    metadata={"path": path, "reason": "no_active_tokens"}
                )
                return self.get_response(request)

            # Strict check for active token
            if not AdminConfig.objects.filter(admin_token=token, is_active=True).exists():
                log_audit_event(
                    request,
                    action=AuditEvent.Action.ADMIN,
                    target_type="admin_access",
                    target_id="unauthorized_token",
                    metadata={"path": path, "reason": "invalid_or_expired_token"}
                )
                raise Http404("Admin URL expired or invalid")

            # Role-based restriction: Authenticated users must be Superadmins or is_superuser
            user = request.user
            if user.is_authenticated:
                if not (user.role == User.Role.SUPERADMIN or user.is_superuser):
                    log_audit_event(
                        request,
                        action=AuditEvent.Action.ADMIN,
                        target_type="admin_access",
                        target_id="denied_role",
                        metadata={"path": path, "username": user.username, "role": user.role}
                    )
                    raise Http404("Admin access restricted to superadmins.")

                # Log successful admin access if this is the start of the session
                if path.endswith(f"/admin_{token}/"):
                   log_audit_event(
                        request,
                        action=AuditEvent.Action.ADMIN,
                        target_type="admin_access",
                        target_id="successful_entry",
                        metadata={"path": path, "username": user.username}
                    )

        return self.get_response(request)
