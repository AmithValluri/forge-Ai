# Forge AI Project Vault — Shared Backend Edition

This package adds a Flask API and SQLite persistence to the Forge AI frontend.

## Run locally
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
python server.py
```
Open http://localhost:8080

## Deploy to Railway
1. Create a new Railway project from this folder/repository.
2. Set the start command to `gunicorn server:app --bind 0.0.0.0:$PORT` (the included Procfile also provides it).
3. Attach a persistent volume and set `DATABASE_PATH=/data/forge_ai.sqlite3`, with the volume mounted at `/data`, so SQLite data survives redeploys.
4. Deploy; Railway will provide a public HTTPS domain.
5. Check `/api/health` on your deployed domain.

## Important prototype caveats
- This demonstrates shared server-side persistence, but the current API stores the app's aggregate state as one JSON document. It is suitable for a challenge demo, not a high-concurrency production system.
- Authentication is demo-only: email lookup is not secure authentication. Do not enter real passwords, sensitive information or real student data.
- Referral counts and project completion state are prototype-level and need server-side validation before using for a real campaign.
- For production, normalize users/referrals/events into separate tables, add secure authentication, rate limiting, CSRF/origin protections, privacy notices and proper admin authorization.
- Local browser storage is used as a fallback if the API is unreachable; the footer indicates whether the shared API is connected.
