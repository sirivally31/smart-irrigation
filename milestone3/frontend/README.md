# Smart Irrigation Assistant PWA

## Run locally

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`. Set `NEXT_PUBLIC_API_BASE_URL` in `frontend/.env.local` when the backend is not on `http://localhost:8000`.

The app includes dashboard, field management, schedules, irrigation history, analytics, alerts, profile/preferences, reports, multilingual UI, voice-query fallback, and PWA installation support. Browser push requires a user click on **Enable browser push** and valid backend VAPID keys. Without provider credentials, SMS, email, Sarvam, and push remain explicitly labeled demo/configuration fallbacks.

## Backend dependency

Start the API from the repository root:

```powershell
python -m uvicorn src.api.app:app --reload --port 8000
```

The service worker does not cache live predictions or API responses as current data. Offline navigation falls back to `public/offline.html`.
