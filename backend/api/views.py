"""HTTP layer only: validate input, call the planner, shape errors."""

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .errors import PlanError, WeatherNeeded
from .planner import plan_trip
from .serializers import PlanRequestSerializer


@api_view(["GET"])
def health(request):
    return Response({"status": "ok", "service": "truck-weather-api"})


@api_view(["POST"])
def plan(request):
    form = PlanRequestSerializer(data=request.data)
    if not form.is_valid():
        message = " ".join(f"{field}: {errors[0]}" for field, errors in form.errors.items())
        return Response({"error": message}, status=400)
    data = form.validated_data
    try:
        return Response(
            plan_trip(
                data["origin"],
                data["destination"],
                data["departure"],
                data["load_lb"],
                int(data["interval_miles"]),
                data["weather"],
            )
        )
    except WeatherNeeded as needed:
        return Response({"weather_request": needed.request})
    except PlanError as exc:
        return Response({"error": str(exc)}, status=422)
