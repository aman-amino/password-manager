from django.http import JsonResponse
from django.shortcuts import render


def home(request):
    return render(request, "app/index.html")


def status(request):
    return JsonResponse({"status": "ok", "endpoints": ["/health/", "/api/vault-items/"]})


def health_check(request):
    return JsonResponse({"status": "ok"})
