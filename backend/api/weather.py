"""Open-Meteo forecast data.

The visitor's browser downloads the forecasts, because free hosting shares IP
addresses and therefore shares Open-Meteo's daily limit. This module says which
data is needed and reads what the browser sends back.
"""

from datetime import timezone

from .errors import PlanError, WeatherNeeded

FIELDS = ["wind_speed_10m", "wind_gusts_10m", "rain", "showers", "snowfall"]


def grid(point):
    """Snap to about 7 miles so nearby points share one lookup."""
    return (round(point[0], 1), round(point[1], 1))


def cell_key(cell):
    return f"{cell[0]:.1f},{cell[1]:.1f}"


def _hour_text(moment):
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:00")


def forecasts(points, start, end, supplied):
    """Return {grid cell: {unix hour: conditions}} from browser-supplied data."""
    cells = sorted({grid(p) for p in points})
    missing = [c for c in cells if cell_key(c) not in supplied]
    if missing:
        raise WeatherNeeded(
            {
                "cells": [{"key": cell_key(c), "lat": c[0], "lon": c[1]} for c in missing],
                "params": {
                    "hourly": ",".join(FIELDS),
                    "wind_speed_unit": "mph",
                    "precipitation_unit": "inch",
                    "timeformat": "unixtime",
                    "timezone": "UTC",
                    "start_hour": _hour_text(start),
                    "end_hour": _hour_text(end),
                },
            }
        )
    try:
        result = {}
        for cell in cells:
            hourly = supplied[cell_key(cell)]
            result[cell] = {
                stamp: {f: hourly[f][n] for f in FIELDS}
                for n, stamp in enumerate(hourly["time"])
            }
        return result
    except (KeyError, IndexError, TypeError):
        raise PlanError("The weather data was incomplete. Please try again.") from None


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
