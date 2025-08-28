from fastapi import FastAPI # type: ignore
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore
from starlette.requests import Request # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
import time
from app.core.config import settings
from app.core.db import engine, SessionLocal  
from sqlalchemy.exc import OperationalError, SQLAlchemyError  
from app.services.bootstrap import ensure_slots  
import logging  

app = FastAPI(
    title="ButtonMap API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

logger = logging.getLogger("buttonmap")
if not logger.handlers:
    logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

app.add_middleware(
    CORSMiddleware, # type: ignore
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "PUT"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = int((start - time.time()) * -1000)
    logger.info("%s %s -> %s in %dms",
                request.method, request.url.path, response.status_code, duration_ms)
    return response

@app.exception_handler(SQLAlchemyError)
async def handle_sqlalchemy_errors(request: Request, exc: SQLAlchemyError):
    logger.exception("DB error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Database error. Please try again later."},
    )

from app.api.v1 import labels as labels_router
app.include_router(labels_router.router, prefix="/api/v1")

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