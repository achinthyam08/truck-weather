class PlanError(Exception):
    """A problem whose message is safe to show to the user."""


class WeatherNeeded(Exception):
    """The client must download these forecasts and send them back."""

    def __init__(self, request):
        super().__init__("Weather data needed")
        self.request = request
