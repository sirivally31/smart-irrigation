# AI-Powered Smart Irrigation System

Milestone 1 implements the data foundation for sensor ingestion and weather integration. It intentionally stops before machine-learning prediction or automated irrigation decisions.

## Objective and Architecture

```text
Sensor simulator or physical sensor -> REST ingestion API -> validation and normalization -> PostgreSQL historical storage
Field coordinates -> OpenWeather service -> normalized weather -> PostgreSQL
```

## Technology Stack

Python, FastAPI, Pydantic, SQLAlchemy, PostgreSQL, Next.js, React, TypeScript, Docker Compose, and Git.

## Project Structure and Database

`backend/app` contains configuration, models, schemas, routers, and the weather service. `database/init.sql` initializes PostgreSQL. `simulator/sensor_simulator.py` sends realistic readings. `frontend/app` contains the functional Milestone 1 page.

Tables are `farmers`, `fields`, `crops`, `sensors`, `sensor_readings`, `weather_data`, and `irrigation_history`. Farmers own fields; fields own crops and sensors; sensors and weather records reference fields. Sensor readings have a unique `(sensor_id, timestamp)` constraint. Weather records retain normalized forecast JSON and a timestamp. Docker seeds one farmer, field, crop, and soil-moisture sensor. The demo field uses latitude `17.3850` and longitude `78.4867`.

## Environment Variables

`POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `DATABASE_URL`, `API_HOST`, `API_PORT`, `CORS_ORIGINS`, `WEATHER_API_KEY`, `WEATHER_API_BASE_URL`, `WEATHER_TIMEOUT_SECONDS`, `NEXT_PUBLIC_API_URL`, `API_URL`, `SENSOR_ID`, and `INTERVAL`.

Copy `.env.example` to `.env`; never commit the real file. `WEATHER_API_KEY` is required only for live weather calls. OpenWeather's current weather and 5-day forecast endpoints are used; `rain` `1h` maps to rainfall and forecast `pop` maps to rain probability as a percentage.

## Running the Project

```powershell
Copy-Item .env.example .env
docker compose up --build
```

The API is at http://localhost:8000, Swagger documentation is at http://localhost:8000/docs, and the frontend is at http://localhost:3000. In another terminal, run `python simulator/sensor_simulator.py` and stop it with Ctrl+C.

For local backend development, install `backend/requirements.txt`, point `DATABASE_URL` at PostgreSQL, and run `uvicorn app.main:app --app-dir backend --reload`.

## Sensor Format and API

The simulator and physical sensors use the same payload:

```json
{"sensor_id":1,"field_id":1,"soil_moisture":42.5,"timestamp":"2026-09-03T10:30:00Z"}
```

`POST /api/v1/sensors/readings` validates IDs, field ownership, numeric moisture from 0 to 100, timezone-aware non-future timestamps, and duplicate timestamps. It returns `201`; duplicate readings return `409`.

`GET /api/v1/sensors/readings?limit=100&sensor_id=1&field_id=1` returns historical readings newest first. `GET /health` returns the API status.

## Configuration and Weather APIs

`POST /api/v1/farmers` and `GET /api/v1/farmers` manage farmers. `POST /api/v1/fields`, `GET /api/v1/fields`, and `GET /api/v1/fields/{field_id}` manage fields with validated coordinates, size, and farmer ownership. `POST /api/v1/fields/{field_id}/crops` and `GET /api/v1/fields/{field_id}/crops` manage crop type, planting date, and growth stage. Sensor configuration is available at `POST` and `GET /api/v1/fields/{field_id}/sensors`.

`GET /api/v1/weather?latitude=17.385&longitude=78.4867` calls OpenWeather and returns normalized temperature, humidity, rainfall, rain probability, forecast, coordinates, and timestamp. `GET /api/v1/fields/{field_id}/weather` resolves coordinates from the field and stores the normalized result in `weather_data`. Missing keys return `503`; provider failures or malformed responses return `502`.

## Validation, Cleaning, and History

Pydantic rejects malformed types, coordinate errors, out-of-range moisture, timezone-less/future timestamps, and invalid weather ranges. UTC normalization provides a consistent timestamp format. Duplicate readings are rejected rather than silently duplicated; abnormal moisture values are rejected rather than hidden. Sensor readings, field configuration, and weather responses are stored historically. No ML, authentication, or automated irrigation control is included.

## Testing and Acceptance

Run `pytest -q backend/tests` after installing requirements. Tests cover timezone normalization, invalid ranges, coordinate validation, and weather schema validation. Manual verification should POST a reading, GET it back, run the simulator for several intervals, and call the field weather endpoint with `WEATHER_API_KEY` configured. Live Docker/database/frontend and external-weather acceptance tests require Docker Desktop, free disk space, installed dependencies, and a valid OpenWeather key.
