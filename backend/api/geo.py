"""Pure geometry helpers. Points are (lat, lon) tuples."""

from bisect import bisect_left
from math import asin, cos, radians, sin, sqrt

EARTH_RADIUS_MILES = 3958.8


def haversine(a, b):
    lat1, lon1, lat2, lon2 = map(radians, (*a, *b))
    h = sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2) ** 2
    return 2 * EARTH_RADIUS_MILES * asin(sqrt(h))


def cumulative_miles(points):
    totals = [0.0]
    for a, b in zip(points, points[1:]):
        totals.append(totals[-1] + haversine(a, b))
    return totals


def point_at(points, totals, mile):
    """Interpolate the position `mile` miles along the line."""
    i = bisect_left(totals, mile)
    if i <= 0:
        return points[0]
    if i >= len(points):
        return points[-1]
    f = (mile - totals[i - 1]) / ((totals[i] - totals[i - 1]) or 1)
    a, b = points[i - 1], points[i]
    return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)


def sample(points, interval_miles):
    """(mile, point) every interval, always including origin and destination."""
    totals = cumulative_miles(points)
    length = totals[-1]
    miles = [0.0]
    while miles[-1] + interval_miles < length - 0.5:
        miles.append(miles[-1] + interval_miles)
    miles.append(length)
    return [(m, point_at(points, totals, m)) for m in miles]


def is_duplicate(a, b, tolerance_miles=2.0, share=0.95):
    """True when nearly all of route `a` runs alongside route `b`."""
    a_samples = [p for _, p in sample(a, 10)]
    b_samples = [p for _, p in sample(b, 2)]
    close = sum(
        any(abs(p[0] - q[0]) < 0.1 and haversine(p, q) <= tolerance_miles for q in b_samples)
        for p in a_samples
    )
    return close / len(a_samples) >= share


def thin(points, max_points=800):
    """Reduce vertices for a lighter response and smoother map."""
    step = max(1, len(points) // max_points)
    thinned = points[::step]
    if thinned[-1] != points[-1]:
        thinned.append(points[-1])
    return thinned
