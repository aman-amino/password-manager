from django import shortcuts
from django.http import Http404
from .models import AdminConfig

class AdminTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if path.startswith('/admin_'):
            # Extract token from path /admin_<token>/...
            parts = path.strip('/').split('/')
            admin_part = parts[0] # The first segment should be admin_<token>

            if admin_part.startswith('admin_'):
                token = admin_part[6:]
                # Bypass check if no tokens exist at all in the database (initial setup)
                if not AdminConfig.objects.exists():
                    return self.get_response(request)

                if not AdminConfig.objects.filter(admin_token=token, is_active=True).exists():
                    raise Http404("Admin URL expired or invalid")

        response = self.get_response(request)
        return response
