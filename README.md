# VoltSense AI

**Know Where Every Watt Goes.** A deterministic, simulated energy-audit prototype for tracking room and appliance electricity use.

## What works

- A React dashboard backed by FastAPI (not static dashboard data)
- Calculated consumption, current load, monthly cost, carbon, and energy-health score
- Daily, room, appliance, and alert views from deterministic simulated readings
- Configurable electricity tariff and carbon-emission factor in `backend/app/config.py`
- Every UI reading is explicitly labelled simulated

## Run locally on Windows

Open two PowerShell terminals from this repository root.

**Backend**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
uvicorn app.main:app --app-dir backend --reload --port 8000
```

**Frontend**

```powershell
cd frontend
npm install
npm run dev
```

Open the URL printed by Vite (normally `http://localhost:5173`). The API is available at `http://127.0.0.1:8000/docs`.

## API

- `GET /api/health`
- `GET /api/dashboard`
- `GET /api/rooms`
- `GET /api/appliances`
