import secrets
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import AdminConfig, User


def is_superadmin(user):
    return user.is_authenticated and (user.role == User.Role.SUPERADMIN or user.is_superuser)


def home(request):
    return render(request, "app/index.html")


def status(request):
    return JsonResponse({"status": "ok", "endpoints": ["/health/", "/api/vault-items/"]})


def health_check(request):
    return JsonResponse({"status": "ok"})


@user_passes_test(is_superadmin)
def rotate_admin_url(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    # Deactivate old tokens
    AdminConfig.objects.all().update(is_active=False)
    # Create new token
    new_token = secrets.token_urlsafe(32)
    AdminConfig.objects.create(admin_token=new_token)

    admin_url = f"/admin_{new_token}/"
    return JsonResponse({"admin_url": admin_url})
