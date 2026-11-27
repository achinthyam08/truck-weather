"""Open-Meteo hourly forecasts, batched and cached in memory."""

import time
from datetime import timezone

import requests
import os

from .errors import PlanError

URL = os.environ.get("OPEN_METEO_URL", "https://api.open-meteo.com/v1/forecast") 
FIELDS = ["wind_speed_10m", "wind_gusts_10m", "rain", "showers", "snowfall"]
BATCH = 100
TTL_SECONDS = 1800
_cache = {}


def grid(point):
    """Snap to about 7 miles so nearby points share one lookup."""
    return (round(point[0], 1), round(point[1], 1))


def _hour_text(moment):
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:00")


def _request(cells, start, end):
    params = {
        "latitude": ",".join(str(c[0]) for c in cells),
        "longitude": ",".join(str(c[1]) for c in cells),
        "hourly": ",".join(FIELDS),
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "timeformat": "unixtime",
        "timezone": "UTC",
        "start_hour": _hour_text(start),
        "end_hour": _hour_text(end),
    }
    try:
        response = requests.get(URL, params=params, timeout=30)
        if response.status_code == 429:
            raise PlanError(f"Weather limit: {response.json().get('reason')}")
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        raise PlanError("The weather service is unavailable. Please try again.") from None
    return data if isinstance(data, list) else [data]


def forecasts(points, start, end):
    """Return {grid cell: {unix hour: conditions}} covering start..end."""
    window = (_hour_text(start), _hour_text(end))
    now = time.time()
    for key in [k for k, (saved, _) in _cache.items() if now - saved > TTL_SECONDS]:
        _cache.pop(key, None)

    cells = sorted({grid(p) for p in points})
    result = {c: _cache[(c, window)][1] for c in cells if (c, window) in _cache}
    missing = [c for c in cells if c not in result]
    for i in range(0, len(missing), BATCH):
        chunk = missing[i : i + BATCH]
        for cell, item in zip(chunk, _request(chunk, start, end)):
            hourly = item["hourly"]
            table = {
                stamp: {f: hourly[f][n] for f in FIELDS}
                for n, stamp in enumerate(hourly["time"])
            }
            _cache[(cell, window)] = (now, table)
            result[cell] = table
    return result


def conditions(tables, point, unix_hour):
    """Conditions at a point and hour. Missing data is an error, never 'Low'."""
    row = tables.get(grid(point), {}).get(unix_hour)
    if row is None or any(row[f] is None for f in FIELDS):
        raise PlanError("Forecast data is missing for part of this trip. Try an earlier departure.")
    return {
        "wind": row["wind_speed_10m"],
        "gust": row["wind_gusts_10m"],
        "rain": round(row["rain"] + row["showers"], 3),
        "snow": row["snowfall"],
    }
