from django.http import JsonResponse


def home(request):
    return JsonResponse({"status": "ok", "endpoints": ["/health/", "/api/vault-items/"]})


def health_check(request):
    return JsonResponse({"status": "ok"})
