from fastapi import FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import datetime, asyncio

from .config  import settings
from .checker import check_port, check_ping

app = FastAPI(
    title="Infra Pulse",
    description="""
Infrastructure Health-Check API.

**Authentication**: pass your API key in the `X-API-Key` header.

Built with FastAPI + Docker. CI/CD via GitHub Actions.

Source: [github.com/avsk-net/infra-pulse](https://github.com)
    """,
    version=settings.app_version,
)

app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

START_TIME = datetime.datetime.utcnow()

# ── API key auth ───────────────────────────────────────────────
api_key_header = APIKeyHeader(name="changeme-use-a-long-random-string", auto_error=False)

async def require_key(key: str = Security(api_key_header)):
    if key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

# ── Models ─────────────────────────────────────────────────────
class BatchItem(BaseModel):
    host: str
    port: int

# ── Routes ─────────────────────────────────────────────────────
@app.get("/", tags=["info"])
def root():
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "docs":    "/docs",
        "health":  "/health",
    }

@app.get("/health", tags=["info"])
def health():
    uptime = str(datetime.datetime.utcnow() - START_TIME)
    return {"status": "healthy", "uptime": uptime, "version": settings.app_version}

@app.get("/api/v1/check/port/{host}/{port}",
         tags=["checks"], dependencies=[Security(require_key)])
def port_check(host: str, port: int):
    if not (1 <= port <= 65535):
        raise HTTPException(400, detail="Port must be 1–65535")
    r = check_port(host, port)
    return {"host": r.host, "port": r.port,
            "reachable": r.reachable, "latency_ms": r.latency_ms,
            "error": r.error,
            "checked_at": datetime.datetime.utcnow().isoformat()}

@app.get("/api/v1/check/ping/{host}",
         tags=["checks"], dependencies=[Security(require_key)])
def ping_check(host: str):
    r = check_ping(host)
    return {"host": r.host, "reachable": r.reachable,
            "latency_ms": r.latency_ms, "error": r.error,
            "checked_at": datetime.datetime.utcnow().isoformat()}

@app.post("/api/v1/batch",
          tags=["checks"], dependencies=[Security(require_key)])
def batch_check(items: List[BatchItem]):
    if len(items) > 20:
        raise HTTPException(400, detail="Max 20 items per batch")
    results = []
    for item in items:
        r = check_port(item.host, item.port)
        results.append({
            "host": r.host, "port": r.port,
            "reachable": r.reachable, "latency_ms": r.latency_ms,
        })
    summary = {"total": len(results),
               "reachable": sum(1 for r in results if r["reachable"]),
               "unreachable": sum(1 for r in results if not r["reachable"])}
    return {"summary": summary, "results": results}
