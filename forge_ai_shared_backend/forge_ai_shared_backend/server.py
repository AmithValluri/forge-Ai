import json
import os
import sqlite3
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory

APP_DIR = Path(__file__).resolve().parent
DB_PATH = os.environ.get("DATABASE_PATH", str(APP_DIR / "forge_ai.sqlite3"))
app = Flask(__name__, static_folder="static")

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS app_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                state_json TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            INSERT OR IGNORE INTO app_state (id, state_json)
            VALUES (1, '{"users":[],"events":[],"votes":{}}')
        """)

@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.get("/api/health")
def health():
    return jsonify({"ok": True, "service": "forge-ai-shared-backend"})

@app.get("/api/state")
def get_state():
    with get_db() as conn:
        row = conn.execute("SELECT state_json FROM app_state WHERE id=1").fetchone()
    return jsonify(json.loads(row["state_json"]))

@app.put("/api/state")
def put_state():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"error": "Expected a JSON object"}), 400
    users = body.get("users", [])
    events = body.get("events", [])
    votes = body.get("votes", {})
    if not isinstance(users, list) or not isinstance(events, list) or not isinstance(votes, dict):
        return jsonify({"error": "Invalid state schema"}), 400
    clean = {"users": users, "events": events, "votes": votes}
    with get_db() as conn:
        conn.execute("""
            INSERT INTO app_state (id, state_json, updated_at)
            VALUES (1, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(id) DO UPDATE SET
              state_json=excluded.state_json,
              updated_at=CURRENT_TIMESTAMP
        """, (json.dumps(clean, separators=(",", ":")),))
    return jsonify({"ok": True})

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
