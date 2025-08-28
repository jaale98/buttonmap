from fastapi import FastAPI # type: ignore
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore

from app.core.config import settings
from app.core.db import engine 

app = FastAPI(
    title="ButtonMap API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
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