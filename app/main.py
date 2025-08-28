from fastapi import FastAPI # type: ignore
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore

from app.core.config import settings
from app.core.db import engine, SessionLocal  
from sqlalchemy.exc import OperationalError  
from app.services.bootstrap import ensure_slots  
import logging  

app = FastAPI(
    title="ButtonMap API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

from app.api.v1 import labels as labels_router
app.include_router(labels_router.router, prefix="/api/v1")

logger = logging.getLogger("buttonmap")
if not logger.handlers:
    logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

@app.on_event("startup")
def seed_labels_if_possible() -> None:
    try:
        db = SessionLocal()
        created = ensure_slots(db, slots=range(1, 11))
        if created:
            logger.info("Bootstrap: created %d label rows.", created)
        else:
            logger.info("Bootstrap: labels already present (no-op).")
    except OperationalError as e:
        logger.warning("Bootstrap skipped: database not available yet (%s)", e.__class__.__name__)
    finally:
        try:
            db.close() # type: ignore
        except Exception:
            pass

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/panel", status_code=302)

@app.get("/admin", include_in_schema=False)
def admin_page() -> HTMLResponse:
    with open("app/static/admin.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/panel", include_in_schema=False)
def panel_page() -> HTMLResponse:
    with open("app/static/panel.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/healthz", tags=["meta"])
def healthz() -> JSONResponse:
    return JSONResponse({"status": "ok", "env": settings.ENV})