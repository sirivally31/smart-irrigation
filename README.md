# Smart Irrigation System

An AI-powered smart irrigation foundation that receives soil-moisture readings from sensors and stores them for later irrigation decisions.

## Week 1 Scope

Week 1 delivers the development environment, PostgreSQL schema, seeded demo entities, validated sensor-reading REST ingestion, a gradual sensor simulator, and a minimal Next.js verification page. Weather integration, advanced data cleaning, field registration, authentication, and ML are intentionally out of scope.

## Architecture

`Sensor -> REST API -> Pydantic validation -> PostgreSQL`

## Technologies

Python, FastAPI, Pydantic, SQLAlchemy, PostgreSQL, Next.js, React, TypeScript, Docker, Docker Compose, and Git/GitHub.

## Setup

1. Clone the repository and enter its directory.
2. Copy `.env.example` to `.env` and change `POSTGRES_PASSWORD`.
3. Start the stack: `docker compose up --build`.
4. Open the frontend at http://localhost:3000 and API docs at http://localhost:8000/docs.
5. To run the simulator outside Docker, use `python simulator/sensor_simulator.py`.

For local backend development, create a Python virtual environment, run `pip install -r backend/requirements.txt`, set `DATABASE_URL` to a reachable PostgreSQL instance, and run `uvicorn app.main:app --app-dir backend --reload`.

## API

`POST /api/v1/sensors/readings`

Request:

```json
{"sensor_id": 1, "field_id": 1, "soil_moisture": 42.5, "timestamp": "2026-09-03T10:30:00Z"}
```

The timestamp must include a timezone and soil moisture must be between 0 and 100. The API verifies that both IDs exist and that the sensor belongs to the field. A successful response is the request plus an assigned `id` and `"status": "stored"`, with HTTP 201.

`GET /api/v1/sensors/readings?limit=100` returns stored readings, newest first.

`GET /health` returns `{ "status": "ok" }`.

## Simulator

The simulator uses the same JSON format as the API, starts at 42.5%, changes gradually, and sends readings continuously. Configure `API_URL`, `SENSOR_ID`, `FIELD_ID`, `INTERVAL`, and optionally `STARTING_MOISTURE` as environment variables. Stop it with Ctrl+C.

## Database

The schema contains `farmers`, `fields`, `crops`, `sensors`, `sensor_readings`, `weather_data`, and `irrigation_history`. Farmers own fields; fields contain crops and sensors; sensors produce readings. Docker initializes the schema and one demo farmer, field, crop, and sensor. The backend also safely creates missing tables and seed records on startup.

## Git

After reviewing the generated files, initialize and commit the actual work with `git init`, `git add .`, and `git commit -m "Implement Week 1 irrigation foundation"`. Add a configured GitHub remote and push with `git push -u origin main` when credentials are available.