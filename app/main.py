import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.logging_config import RequestLoggingMiddleware, configure_logging
from app.models import Asset, CreateAssetRequest, EmployeeActionRequest, HealthResponse
from app.store import AssetStore

configure_logging()

logger = logging.getLogger("asset_service.app")
store = AssetStore()

app = FastAPI(title="资产借用和归还服务", version="1.0.0")
app.add_middleware(RequestLoggingMiddleware)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("Asset service started asset_count=%s", store.asset_count())


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", asset_count=store.asset_count())


@app.get("/api/assets", response_model=list[Asset])
async def list_assets() -> list[Asset]:
    return store.list_assets()


@app.post("/api/assets", response_model=Asset, status_code=201)
async def create_asset(payload: CreateAssetRequest) -> Asset:
    return store.create_asset(payload)


@app.post("/api/assets/{asset_id}/borrow", response_model=Asset)
async def borrow_asset(asset_id: str, payload: EmployeeActionRequest) -> Asset:
    return store.borrow_asset(asset_id, payload.employee_id)


@app.post("/api/assets/{asset_id}/return", response_model=Asset)
async def return_asset(asset_id: str, payload: EmployeeActionRequest) -> Asset:
    return store.return_asset(asset_id, payload.employee_id)
