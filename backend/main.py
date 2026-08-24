from fastapi import FastAPI, status, Response
from contextlib import asynccontextmanager
import redis.asyncio as redis
import aiosqlite
import os

from dotenv import load_dotenv
load_dotenv()

from db.migrations import run_migrations
from shadowmesh.core import ShadowMeshCore
from shadowmesh.topology import TopologyGenerator
from shadowmesh.registry import IdentityRegistry

from mirrortrap.session_manager import SessionManager
from mirrortrap.profile_engine import ProfileEngine
from mirrortrap.dossier_generator import DossierGenerator

from pydantic import BaseModel
import time
import uuid
import datetime
import random
import string

REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))

DB_PATH = os.environ.get("SQLITE_DB_PATH", "/data/phantasm.db")
if DB_PATH.startswith("/data"):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    DB_PATH = os.path.join(project_root, "data", "phantasm.db")

shadowmesh_engine = None
registry = None
topology_generator = None

session_manager = None
profile_engine = None
dossier_generator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global shadowmesh_engine, registry, topology_generator
    global session_manager, profile_engine, dossier_generator
    # Run DB migrations on startup
    await run_migrations()
    
    registry = IdentityRegistry(DB_PATH)
    await registry.initialize()
    
    topology_generator = TopologyGenerator()
    shadowmesh_engine = ShadowMeshCore(registry, topology_generator.topology)
    
    session_manager = SessionManager()
    profile_engine = ProfileEngine(session_manager)
    dossier_generator = DossierGenerator()
    
    yield
    # Cleanup on shutdown
    if shadowmesh_engine:
        await shadowmesh_engine.stop()

app = FastAPI(title="PHANTASM API", lifespan=lifespan)

@app.get("/api/health")
async def health_check(response: Response):
    health_status = {
        "status": "ok",
        "components": {
            "sqlite": "ok",
            "redis": "ok"
        },
        "version": "1.0.0-phase1"
    }
    
    # Check SQLite
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("SELECT 1")
            await cursor.fetchone()
    except Exception as e:
        health_status["components"]["sqlite"] = "error"
        health_status["status"] = "error"
        
    # Check Redis
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, socket_timeout=2)
        await r.ping()
        await r.close()
    except Exception as e:
        health_status["components"]["redis"] = "error"
        health_status["status"] = "error"

    if health_status["status"] == "error":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return health_status

@app.post("/api/shadowmesh/start")
async def start_shadowmesh():
    if shadowmesh_engine and not shadowmesh_engine.running:
        await shadowmesh_engine.start()
        return {"status": "started"}
    return {"status": "already_running"}

@app.post("/api/shadowmesh/stop")
async def stop_shadowmesh():
    if shadowmesh_engine and shadowmesh_engine.running:
        await shadowmesh_engine.stop()
        return {"status": "stopped"}
    return {"status": "already_stopped"}

@app.get("/api/shadowmesh/status")
async def get_shadowmesh_status():
    is_running = shadowmesh_engine.running if shadowmesh_engine else False
    pkt_count = shadowmesh_engine.packet_count if shadowmesh_engine else 0
    node_count = len(topology_generator.topology["nodes"]) if topology_generator else 0
    return {
        "status": "running" if is_running else "stopped",
        "intercepted_packets": pkt_count,
        "topology_nodes": node_count,
        "demo_mode": shadowmesh_engine.demo_mode if shadowmesh_engine else False
    }

@app.get("/api/shadowmesh/topology")
async def get_topology():
    if topology_generator:
        return topology_generator.get_topology()
    return {"nodes": [], "edges": [], "subnets": []}

class SessionCommandRequest(BaseModel):
    session_id: str
    raw_command: str
    source_ip: str
    timestamp_ms: int

@app.post("/api/session/start")
async def start_session():
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M%S")
    rand_chars = ''.join(random.choices(string.ascii_uppercase, k=6))
    session_id = f"PH-2026-{ts}-{rand_chars}"
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO sessions (session_id, created_at, session_state) VALUES (?, datetime('now'), 'active')",
            (session_id,)
        )
        await db.commit()
        
    session_manager.create_session(session_id)
    return {"session_id": session_id, "status": "started"}

@app.post("/api/session/command")
async def process_session_command(req: SessionCommandRequest):
    session = session_manager.get_session(req.session_id)
    if not session:
        return Response(status_code=404)
        
    cmds = session["commands"]
    ici_ms = 0
    if cmds:
        last_ts = cmds[-1].get("timestamp_ms", req.timestamp_ms)
        ici_ms = req.timestamp_ms - last_ts
        
    command_event = {
        "raw_command": req.raw_command,
        "source_ip": req.source_ip,
        "timestamp_ms": req.timestamp_ms,
        "ici_ms": max(0, ici_ms)
    }
    
    profile_update = await profile_engine.process_command(req.session_id, command_event)
    return profile_update

@app.get("/api/session/{session_id}/profile")
async def get_session_profile(session_id: str):
    session = session_manager.get_session(session_id)
    if not session:
        return Response(status_code=404)
        
    return session["profile"]

@app.get("/api/session/{session_id}/dossier")
async def get_session_dossier(session_id: str):
    session_manager.end_session(session_id)
    
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT created_at FROM sessions WHERE session_id = ?", (session_id,))
        row = await cursor.fetchone()
        if row:
            sess = session_manager.get_session(session_id)
            if not sess:
                return Response(status_code=404)
            duration = int(sess.get("end_time", time.time()) - sess["start_time"])
            
            await db.execute(
                "UPDATE sessions SET session_state = 'ended', ended_at = datetime('now'), duration_seconds = ? WHERE session_id = ?",
                (duration, session_id)
            )
            await db.commit()
            
    dossier = await dossier_generator.generate_dossier(session_id)
    return dossier

