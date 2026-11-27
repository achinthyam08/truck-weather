# Weather-Aware Truck Routing

Build a React + Django web app that helps a truck driver choose the safest route based on
weather, load weight and travel time. Correctness, clarity and smoothness over extra features.

## Inputs
Origin, destination, departure date/time, load weight (lb), sampling interval (10 / 25 / 50 miles).

## Stack
- Frontend: React (Vite), react-leaflet, OpenStreetMap tiles. Deploy on Vercel.
- Backend: Django + Django REST Framework, no database models. Deploy on Render.
- Routing and geocoding: TomTom (key only in backend environment variable TOMTOM_API_KEY).
- Weather: Open-Meteo (no key). Show "Weather data by Open-Meteo.com".

## Features
1. Generate 3 route options.
2. Sample weather at each checkpoint using the truck's estimated arrival time there.
3. Classify risk with the rules below.
4. Recommend the best route.
5. Map with all routes, checkpoints, risk levels, ETAs and route summaries.
6. Weather heatmap along the trip corridor with a 0-48 hour forecast slider.

## Routing
- GET https://api.tomtom.com/routing/1/calculateRoute/{lat,lon}:{lat,lon}/json
  with travelMode=truck, maxAlternatives=2, departAt, vehicleWeight (kg), key.
- vehicleWeight = (load + 35,000 lb assumed empty truck) converted to kg.
- Geocoding: GET https://api.tomtom.com/search/2/geocode/{query}.json
- If fewer than 3 routes return, request extra routes through an offset via-point.
  Discard near-duplicates. If still fewer than 3, show what exists and say so.

## Checkpoints and weather
- Place checkpoints every N miles along the route geometry, plus origin and destination.
- ETA = departure + travel time to that point (proportional to route distance).
- Use UTC internally; show local time in the UI.
- Open-Meteo hourly: wind_speed_10m, wind_gusts_10m, rain, showers, snowfall;
  wind_speed_unit=mph, precipitation_unit=inch, timezone=UTC.
- Rain rate = rain + showers. Precipitation values cover the preceding hour,
  so use the first hourly timestamp at or after the ETA.
- Batch many coordinates per request and cache responses.
- If an ETA is beyond the forecast range, return a clear error. Never treat missing data as Low.

## Risk rules
Levels: Low=0, Moderate=1, High=2, Severe=3, No Travel=4.

| Condition | Low | Moderate | High | Severe | No Travel |
|---|---|---|---|---|---|
| Wind (mph) | <25 | 25 to <35 | 35 to <45 | 45 to <55 | >=55 |
| Rain (in/hr) | <0.10 | 0.10 to <0.25 | 0.25 to <0.50 | 0.50 to 1.00 | >1.00 |
| Snow (in/hr) | <0.5 | 0.5 to <1.0 | 1.0 to <2.0 | 2.0 to 3.0 | >3.0 |

Load rules (wind):
- >=55 mph: No Travel for any load
- 45 to <55 mph and load >30,000 lb: No Travel
- 35 to <45 mph and load >40,000 lb: Severe

Checkpoint risk = worst of wind, rain, snow and load rules.
Wind means sustained speed; gusts are shown for information only.

## Recommendation
Each checkpoint's level applies to the miles halfway to its neighbours.
Sort routes by, in order:
1. Fewest No Travel miles (assumption: added because it is worse than Severe)
2. Fewest Severe miles
3. Fewest High miles
4. Lowest distance-weighted average risk
5. Shortest travel time

Round miles to whole numbers and average risk to 2 decimals before comparing.
Explain in the UI why the route was chosen. If every route has No Travel miles,
warn the driver to delay departure.

## Heatmap
- Sample points along all three routes (the corridor).
- Slider hour 0 = departure time, up to +48.
- Fetch all 49 hours once; moving the slider must not call the API.
- Draw translucent circles coloured by risk level.

## Quality
- Risk and ranking logic are pure functions with unit tests, including every boundary.
- Separate modules for routing, weather, checkpoints, risk and ranking.
- Loading and error states. No secrets in Git.
- README: setup, architecture, assumptions, limitations.
