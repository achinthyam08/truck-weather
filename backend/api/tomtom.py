"""TomTom geocoding and truck routing."""

import os
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

import requests

from . import geo
from .errors import PlanError

BASE = "https://api.tomtom.com"
EMPTY_TRUCK_LB = 35_000
KG_PER_LB = 0.45359237


def _get(url, params):
    key = os.environ.get("TOMTOM_API_KEY")
    if not key:
        raise PlanError("TOMTOM_API_KEY is not set on the server.")
    try:
        response = requests.get(url, params={**params, "key": key}, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        # Never echo the exception: its URL contains the API key.
        status = getattr(exc.response, "status_code", "no response")
        raise PlanError(f"TomTom request failed ({status}).") from None


def geocode(query):
    data = _get(f"{BASE}/search/2/geocode/{quote(query, safe='')}.json", {"limit": 1})
    if not data.get("results"):
        raise PlanError(f"Could not find the location: {query}")
    result = data["results"][0]
    position = result["position"]
    return {
        "label": result["address"].get("freeformAddress", query),
        "lat": position["lat"],
        "lon": position["lon"],
    }


def _calculate(stops, departure, load_lb, alternatives):
    locations = ":".join(f"{lat},{lon}" for lat, lon in stops)
    params = {
        "travelMode": "truck",
        "vehicleCommercial": "true",
        "vehicleWeight": round((load_lb + EMPTY_TRUCK_LB) * KG_PER_LB),
    }
    if alternatives:
        params["maxAlternatives"] = alternatives
    # TomTom only accepts future departure times.
    if departure > datetime.now(timezone.utc) + timedelta(minutes=2):
        params["departAt"] = departure.strftime("%Y-%m-%dT%H:%M:%SZ")
    data = _get(f"{BASE}/routing/1/calculateRoute/{locations}/json", params)
    return [
        {
            "points": [(p["latitude"], p["longitude"]) for leg in r["legs"] for p in leg["points"]],
            "miles": r["summary"]["lengthInMeters"] / 1609.344,
            "seconds": r["summary"]["travelTimeInSeconds"],
        }
        for r in data.get("routes", [])
    ]


def _via_points(origin, destination):
    """Points offset to either side of the straight line's midpoint."""
    mid_lat, mid_lon = (origin[0] + destination[0]) / 2, (origin[1] + destination[1]) / 2
    d_lat, d_lon = destination[0] - origin[0], destination[1] - origin[1]
    for factor in (0.12, -0.12, 0.25, -0.25):
        yield (mid_lat - d_lon * factor, mid_lon + d_lat * factor)


def three_routes(origin, destination, departure, load_lb):
    routes = []

    def add(candidates):
        for c in candidates:
            if len(routes) < 3 and not any(geo.is_duplicate(c["points"], r["points"]) for r in routes):
                routes.append(c)

    add(_calculate([origin, destination], departure, load_lb, 2))
    if not routes:
        raise PlanError("No truck route found between these locations.")
    for via in _via_points(origin, destination):
        if len(routes) >= 3:
            break
        try:
            add(_calculate([origin, via, destination], departure, load_lb, 0))
        except PlanError:
            continue  # the via point may be unreachable (water, border)
    return routes
