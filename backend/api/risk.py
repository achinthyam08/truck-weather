"""Pure risk classification rules. No I/O."""

LOW, MODERATE, HIGH, SEVERE, NO_TRAVEL = range(5)
LABELS = ["Low", "Moderate", "High", "Severe", "No Travel"]


def wind_level(mph):
    if mph >= 55:
        return NO_TRAVEL
    if mph >= 45:
        return SEVERE
    if mph >= 35:
        return HIGH
    if mph >= 25:
        return MODERATE
    return LOW


def _precip_level(rate, moderate, high, severe, severe_max):
    if rate > severe_max:
        return NO_TRAVEL
    if rate >= severe:
        return SEVERE
    if rate >= high:
        return HIGH
    if rate >= moderate:
        return MODERATE
    return LOW


def rain_level(inches_per_hour):
    return _precip_level(inches_per_hour, 0.10, 0.25, 0.50, 1.00)


def snow_level(inches_per_hour):
    return _precip_level(inches_per_hour, 0.5, 1.0, 2.0, 3.0)


def load_level(wind_mph, load_lb):
    """Extra wind restrictions for heavy loads."""
    if wind_mph >= 55 or (wind_mph >= 45 and load_lb > 30_000):
        return NO_TRAVEL
    if wind_mph >= 35 and load_lb > 40_000:
        return SEVERE
    return LOW


def classify(wind_mph, rain, snow, load_lb):
    """Overall level is the worst of all rules."""
    return max(
        wind_level(wind_mph),
        rain_level(rain),
        snow_level(snow),
        load_level(wind_mph, load_lb),
    )
