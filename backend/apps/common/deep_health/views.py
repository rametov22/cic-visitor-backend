import hmac

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .checks import build_deep_health_report


@require_GET
def deep_health(request):
    expected_key = settings.DEEP_HEALTH_API_KEY
    supplied_key = request.headers.get("X-API-Key", "")
    if not expected_key or not supplied_key or not hmac.compare_digest(supplied_key, expected_key):
        response = JsonResponse({"detail": "Unauthorized"}, status=401)
        response["Cache-Control"] = "no-store"
        return response

    response = JsonResponse(build_deep_health_report(), status=200)
    response["Cache-Control"] = "no-store"
    return response
