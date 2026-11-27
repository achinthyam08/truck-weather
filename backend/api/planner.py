"""Combine routing, checkpoints, weather, risk and ranking into one plan."""

from datetime import datetime, timedelta, timezone
from functools import lru_cache
from math import ceil

from . import geo, ranking, risk, tomtom, weather
from .errors import PlanError

HEATMAP_HOURS = 48
HEATMAP_SPACING_MILES = 30
FORECAST_LIMIT = timedelta(days=15)


def next_hour(moment):
    """First forecast hour at or after `moment`, as a unix timestamp."""
    return ceil(moment.timestamp() / 3600) * 3600


def _iso(moment):
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@lru_cache(maxsize=16)
def find_routes(origin_text, destination_text, departure, load_lb):
    """Cached so the follow-up request with weather reuses identical routes."""
    origin = tomtom.geocode(origin_text)
    destination = tomtom.geocode(destination_text)
    routes = tomtom.three_routes(
        (origin["lat"], origin["lon"]), (destination["lat"], destination["lon"]), departure, load_lb
    )
    return origin, destination, routes


def plan_trip(origin_text, destination_text, departure, load_lb, interval_miles, weather_data):
    origin, destination, routes = find_routes(origin_text, destination_text, departure, load_lb)

    longest = timedelta(seconds=max(r["seconds"] for r in routes))
    end = departure + max(longest, timedelta(hours=HEATMAP_HOURS)) + timedelta(hours=1)
    if end > datetime.now(timezone.utc) + FORECAST_LIMIT:
        raise PlanError("The trip extends beyond the available forecast. Choose an earlier departure.")

    checkpoints = [geo.sample(r["points"], interval_miles) for r in routes]
    corridor = {}
    for r in routes:
        for _, point in geo.sample(r["points"], HEATMAP_SPACING_MILES):
            corridor[weather.grid(point)] = point

    every_point = [p for route in checkpoints for _, p in route] + list(corridor.values())
    tables = weather.forecasts(every_point, departure, end, weather_data)

    results, summaries = [], []
    for index, (route, samples) in enumerate(zip(routes, checkpoints)):
        length = samples[-1][0] or 1
        scale = route["miles"] / length  # align with TomTom's road distance
        stops = []
        for mile, point in samples:
            eta = departure + timedelta(seconds=route["seconds"] * mile / length)
            now = weather.conditions(tables, point, next_hour(eta))
            stops.append(
                {
                    "mile": round(mile * scale, 1),
                    "lat": point[0],
                    "lon": point[1],
                    "eta": _iso(eta),
                    **now,
                    "level": risk.classify(now["wind"], now["rain"], now["snow"], load_lb),
                }
            )
        summary = ranking.score(
            [mile * scale for mile, _ in samples],
            [s["level"] for s in stops],
            route["seconds"] / 3600,
        )
        summaries.append(summary)
        results.append(
            {
                "id": index,
                "name": f"Route {chr(65 + index)}",
                "miles": round(route["miles"], 1),
                "arrival": _iso(departure + timedelta(seconds=route["seconds"])),
                "geometry": geo.thin(route["points"]),
                "checkpoints": stops,
                "summary": summary,
            }
        )

    start_hour = next_hour(departure)
    heatmap = []
    for point in corridor.values():
        levels = []
        for hour in range(HEATMAP_HOURS + 1):
            c = weather.conditions(tables, point, start_hour + hour * 3600)
            levels.append(risk.classify(c["wind"], c["rain"], c["snow"], load_lb))
        heatmap.append({"lat": point[0], "lon": point[1], "levels": levels})

    order = ranking.rank(summaries)
    warnings = []
    if len(results) < 3:
        warnings.append(f"Only {len(results)} distinct route(s) could be generated.")
    if all(s["max_level"] == risk.NO_TRAVEL for s in summaries):
        warnings.append("Every route has No Travel conditions. Delay your departure.")
    elif summaries[order[0]]["max_level"] == risk.NO_TRAVEL:
        warnings.append("The recommended route has a No Travel checkpoint. Review it before driving.")

    return {
        "origin": origin,
        "destination": destination,
        "departure": _iso(departure),
        "heatmap_start": _iso(datetime.fromtimestamp(start_hour, timezone.utc)),
        "routes": results,
        "recommended_id": order[0],
        "reason": ranking.explain(summaries, order),
        "heatmap": heatmap,
        "warnings": warnings,
    }
