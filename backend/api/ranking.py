"""Pure route scoring and recommendation. No I/O."""

from .risk import HIGH, NO_TRAVEL, SEVERE

CRITERIA = [
    ("no_travel_miles", "fewest No Travel miles"),
    ("severe_miles", "fewest Severe miles"),
    ("high_miles", "fewest High miles"),
    ("average_risk", "lowest average risk"),
    ("duration_hours", "shortest travel time"),
]


def segment_miles(positions):
    """Miles each checkpoint represents: halfway to each neighbour."""
    last = len(positions) - 1
    return [
        (positions[min(i + 1, last)] - positions[max(i - 1, 0)]) / 2
        for i in range(len(positions))
    ]


def score(positions, levels, duration_hours):
    miles = segment_miles(positions)
    total = sum(miles)

    def miles_at(level):
        return round(sum(m for m, lv in zip(miles, levels) if lv == level))

    average = sum(m * lv for m, lv in zip(miles, levels)) / total if total else max(levels)
    return {
        "no_travel_miles": miles_at(NO_TRAVEL),
        "severe_miles": miles_at(SEVERE),
        "high_miles": miles_at(HIGH),
        "average_risk": round(average, 2),
        "duration_hours": round(duration_hours, 2),
        "max_level": max(levels),
    }


def _key(summary):
    return tuple(summary[name] for name, _ in CRITERIA)


def rank(summaries):
    """Return route indexes from best to worst."""
    return sorted(range(len(summaries)), key=lambda i: _key(summaries[i]))


def explain(summaries, order):
    if len(order) < 2:
        return "Only one route is available."
    best, runner_up = summaries[order[0]], summaries[order[1]]
    for name, text in CRITERIA:
        if best[name] != runner_up[name]:
            return f"Chosen for {text} ({best[name]} vs {runner_up[name]} for the next best)."
    return "The top routes are equal on every criterion."
