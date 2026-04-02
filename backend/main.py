import os
import sys
import json
import asyncio
import subprocess
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_connection, get_stats

# ── CONFIG ──────────────────────────────────────────────
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, "data", "reports")
# ────────────────────────────────────────────────────────

app = FastAPI(title="ExForge API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── WebSocket connection manager ──
class ConnectionManager:
    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active.remove(ws)

    async def broadcast(self, message: str):
        for ws in self.active:
            try:
                await ws.send_text(message)
            except:
                pass

manager = ConnectionManager()
pipeline_running = False


# ── Models ──
class NicheItem(BaseModel):
    niche:    str
    location: str
    active:   bool

class ConfigUpdate(BaseModel):
    search_queries:    List[NicheItem]
    max_results:       int
    run_time:          str
    daily_email_limit: int


# ── Config endpoints ──
@app.get("/config")
def get_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)

@app.post("/config")
def update_config(config: ConfigUpdate):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config.dict(), f, indent=2)
    return {"status": "saved"}


# ── Stats endpoint ──
@app.get("/stats")
def get_dashboard_stats():
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM leads")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT status, COUNT(*) FROM leads GROUP BY status")
    by_status = dict(cursor.fetchall())

    cursor.execute("SELECT COUNT(*) FROM leads WHERE status='emailed'")
    total_sent = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM leads
        WHERE status='emailed'
        AND date(emailed_at) = date('now')
    """)
    sent_today = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM leads
        WHERE status='emailed'
        AND emailed_at >= date('now', '-7 days')
    """)
    sent_week = cursor.fetchone()[0]

    conn.close()

    return {
        "total_leads":  total,
        "by_status":    by_status,
        "total_sent":   total_sent,
        "sent_today":   sent_today,
        "sent_week":    sent_week,
        "pipeline_running": pipeline_running,
    }


# ── Leads endpoints ──
@app.get("/leads")
def get_leads(status: Optional[str] = None, limit: int = 100):
    conn   = get_connection()
    cursor = conn.cursor()

    if status:
        cursor.execute("""
            SELECT id, name, category, address, phone, website,
                   rating, reviews, status, ai_score, ai_reason,
                   email, emailed_at, scraped_at
            FROM leads WHERE status = ? ORDER BY id DESC LIMIT ?
        """, (status, limit))
    else:
        cursor.execute("""
            SELECT id, name, category, address, phone, website,
                   rating, reviews, status, ai_score, ai_reason,
                   email, emailed_at, scraped_at
            FROM leads ORDER BY id DESC LIMIT ?
        """, (limit,))

    rows    = cursor.fetchall()
    columns = ["id", "name", "category", "address", "phone", "website",
               "rating", "reviews", "status", "ai_score", "ai_reason",
               "email", "emailed_at", "scraped_at"]
    conn.close()

    return [dict(zip(columns, row)) for row in rows]


@app.get("/leads/sent")
def get_sent_leads():
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, email, website, emailed_at, ai_score
        FROM leads WHERE status='emailed'
        ORDER BY emailed_at DESC
    """)
    rows    = cursor.fetchall()
    columns = ["id", "name", "email", "website", "emailed_at", "ai_score"]
    conn.close()
    return [dict(zip(columns, row)) for row in rows]


# ── Reports endpoint ──
@app.get("/reports")
def list_reports():
    if not os.path.exists(REPORTS_DIR):
        return []
    files = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".pdf")]
    return [{"filename": f, "url": f"/reports/download/{f}"} for f in files]

@app.get("/reports/download/{filename}")
def download_report(filename: str):
    path = os.path.join(REPORTS_DIR, filename)
    if os.path.exists(path):
        return FileResponse(path, media_type="application/pdf", filename=filename)
    return {"error": "File not found"}


# ── Pipeline control endpoints ──
async def run_module(module: str):
    global pipeline_running
    pipeline_running = True

    await manager.broadcast(json.dumps({
        "type": "log",
        "message": f"Starting {module}...",
        "time": datetime.now().strftime("%H:%M:%S")
    }))

    try:
        main_py = os.path.join(BASE_DIR, "main.py")
        process = await asyncio.create_subprocess_exec(
            sys.executable, main_py, f"--{module}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=BASE_DIR
        )

        async for line in process.stdout:
            text = line.decode("utf-8", errors="replace").rstrip()
            if text:
                await manager.broadcast(json.dumps({
                    "type": "log",
                    "message": text,
                    "time": datetime.now().strftime("%H:%M:%S")
                }))

        await process.wait()

    except Exception as e:
        await manager.broadcast(json.dumps({
            "type": "error",
            "message": str(e),
            "time": datetime.now().strftime("%H:%M:%S")
        }))
    finally:
        pipeline_running = False
        await manager.broadcast(json.dumps({
            "type": "done",
            "message": f"{module} complete",
            "time": datetime.now().strftime("%H:%M:%S")
        }))


@app.post("/pipeline/run")
async def run_pipeline(background_tasks: BackgroundTasks):
    if pipeline_running:
        return {"status": "already_running"}
    background_tasks.add_task(run_module, "now")
    return {"status": "started"}

@app.post("/pipeline/{module}")
async def run_single_module(module: str, background_tasks: BackgroundTasks):
    valid = ["scrape", "shortlist", "audit", "report", "compose", "send"]
    if module not in valid:
        return {"error": f"Invalid module. Choose from: {valid}"}
    if pipeline_running:
        return {"status": "already_running"}
    background_tasks.add_task(run_module, module)
    return {"status": "started", "module": module}


# ── WebSocket for live logs ──
@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)