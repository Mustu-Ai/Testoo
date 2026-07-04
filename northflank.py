"""
Deploy this on Northflank as a minimal FastAPI service.
It exposes two endpoints used by the periodic checker running on HF:

  GET /ping                -> confirms Northflank itself is reachable from HF
  GET /check-telegram      -> confirms Northflank -> api.telegram.org works

Run locally:  uvicorn northflank_test_server:app --host 0.0.0.0 --port 8000
requirements.txt should contain: fastapi, uvicorn, httpx
"""

from datetime import datetime, timezone
import httpx
from fastapi import FastAPI

app = FastAPI()

# Optional: set your real bot token as an env var on Northflank to test
# outbound connectivity to Telegram FROM Northflank as well.
import os
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")


@app.get("/ping")
async def ping():
    return {
        "status": "ok",
        "source": "northflank",
        "time_utc": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/check-telegram")
async def check_telegram():
    if not BOT_TOKEN:
        return {"status": "skipped", "reason": "no TELEGRAM_BOT_TOKEN set"}
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
        return {
            "status": "ok" if resp.status_code == 200 else "error",
            "http_status": resp.status_code,
            "time_utc": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "time_utc": datetime.now(timezone.utc).isoformat(),
        }
