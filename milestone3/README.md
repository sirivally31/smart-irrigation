# Milestone 3: Smart Irrigation Assistant

This repository contains the Milestone 2 ML irrigation engine plus a Milestone 3 FastAPI backend and mobile-first Next.js farmer PWA. Existing joblib models, datasets, and preprocessing remain unchanged.

## Windows setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.pipeline
copy .env.example .env
```

Start the backend:

```powershell
python -m uvicorn src.api.app:app --reload --port 8000
```

In another terminal, start the frontend:

```powershell
cd frontend
npm install
copy .env.example .env.local
npm run dev
```

Open `http://localhost:3000`. The API documentation is available at `http://localhost:8000/docs`.

## Milestone 3 features

- Farmer dashboard, profile, notification preferences, field CRUD, schedules, execution history, analytics, alerts, and PDF/CSV reports.
- ML recommendations use the existing preprocessing and model feature order. Recommendations are distinct from completed irrigation records.
- English, Hindi, and Kannada static UI translations, plus backend Sarvam integration with a domain fallback when no key is configured.
- Voice query UI with browser speech recognition where supported and text fallback otherwise.
- Rule-based low-moisture, rainfall, stale-data, over-watering, reminder, and ML alerts with read/dismiss controls and duplicate suppression.
- PWA manifest, install prompt, offline navigation fallback, and user-triggered Web Push subscription flow.

## External integrations and demo mode

Provider credentials belong only in the backend `.env`. Empty or placeholder Sarvam, VAPID, Twilio, and SendGrid values keep the application in clearly labeled demo/fallback mode; they do not represent real delivery. Valid VAPID keys are required for browser push, while Twilio and SendGrid require verified sender/recipient configuration.

Important environment variables are documented in `.env.example`. Frontend configuration is limited to `NEXT_PUBLIC_API_BASE_URL` in `frontend/.env.example`.

## Testing

```powershell
python -m pytest tests/test_backend.py -q
cd frontend
npm run build
```

The frontend production build is verified in this workspace. Install the Python requirements in the active virtual environment before running the backend test suite.
