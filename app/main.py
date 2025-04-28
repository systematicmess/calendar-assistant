from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware          # ← add this

from .api.routers import auth, calendar, agent

app = FastAPI(title="Calendar Assistant API", version="0.1.0")

# ──────────────────────────────────────────────────────────────
# CORS: allow the Vite dev server (ports 5173-5175) to call the API
# ──────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ──────────────────────────────────────────────────────────────

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(calendar.router, prefix="/cal", tags=["calendar"])
app.include_router(agent.router, prefix="/agent", tags=["agent"])


@app.get("/healthz", tags=["meta"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
