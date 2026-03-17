from django import shortcuts
from django.http import Http404
from .models import AdminConfig
from vault.utils import log_audit_event
from vault.models import AuditEvent

class AdminTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if '/admin_' in path:
            # Extract token from path .../admin_<token>/...
            parts = path.split('/')
            admin_part = next((p for p in parts if p.startswith('admin_')), None)
            if admin_part:
                if admin_part.startswith('admin_'):
                    token = admin_part[6:]
                    # Bypass check if no active tokens exist yet (initial setup)
                    if not AdminConfig.objects.filter(is_active=True).exists():
                        response = self.get_response(request)
                        return response
                    if not AdminConfig.objects.filter(admin_token=token, is_active=True).exists():
                        log_audit_event(
                            request,
                            action=AuditEvent.Action.ADMIN,
                            target_type="admin_access",
                            target_id="unauthorized",
                            metadata={"path": path, "reason": "invalid_or_expired_token"}
                        )
                        raise Http404("Admin URL expired or invalid")

        response = self.get_response(request)
        return response
