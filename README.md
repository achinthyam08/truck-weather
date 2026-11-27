# Weather-Aware Truck Routing

React + Django app that compares truck routes by forecast weather risk, load weight and travel time.

## Run locally (Windows PowerShell)

Backend:

    cd backend
    py -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    python manage.py runserver

Create `backend/.env` from `.env.example` and set `TOMTOM_API_KEY`.

Frontend (second terminal):

    cd frontend
    npm install
    npm run dev

Tests: `python manage.py test api` (from `backend`).

## Architecture
- `api/tomtom.py`: geocoding and truck routes
- `api/geo.py`: checkpoints and route de-duplication
- `api/weather.py`: batched, cached Open-Meteo forecasts
- `api/risk.py`, `api/ranking.py`: pure, tested rules
- `api/planner.py`: combines the above
- `frontend/src`: form, route cards, map and forecast slider

One `POST /api/plan` call returns routes, checkpoints and 49 hours of heatmap data,
so the slider needs no further requests.

## Assumptions
- Empty truck weight is 35,000 lb, added to the load for routing.
- Overall risk is the worst of wind, rain, snow and load rules.
- Range boundaries belong to the higher band, except exactly 1.00 in/hr rain and 3.0 in/hr snow (Severe).
- Wind is sustained 10 m wind. Gusts are shown but not scored.
- No Travel miles are minimised before Severe miles.
- Each checkpoint covers the road halfway to its neighbours.
- Weather is read at the first forecast hour at or after the ETA.
- Slider hour 0 is the first full hour at or after departure.

## Limitations
- ETAs assume constant average speed and no rest breaks.
- Weather locations are rounded to 0.1 degree.
- Fewer than three distinct routes may exist; the app says so.
- If TomTom returns too few alternatives, routes via offset points may include detours.
- Very long trips at 10 mile spacing can hit Open-Meteo rate limits.
- The free Render server is slow to respond after being idle.
- Not a substitute for official road and weather advisories.

Built with AI assistance. Weather data by [Open-Meteo.com](https://open-meteo.com/).
