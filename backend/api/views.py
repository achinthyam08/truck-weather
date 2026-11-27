"""
GET /api/health

Returns:
    {
        "status": "ok",
        "version": "1.0.0",
        "service": "truck-weather-api"
    }
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def health(request):
    """Liveness check used by the frontend and deployment platform."""
    return Response(
        {
            "status": "ok",
            "version": "1.0.0",
            "service": "truck-weather-api",
        }
    )
