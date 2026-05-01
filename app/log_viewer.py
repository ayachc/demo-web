from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse

LOG_FILE = Path(__file__).resolve().parent.parent / "logs" / "app.log"

app = FastAPI(title="资产服务日志查看子服务", version="1.0.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/logs/app", response_class=PlainTextResponse)
async def read_app_log() -> PlainTextResponse:
    if not LOG_FILE.exists():
        return PlainTextResponse("logs/app.log does not exist yet.\n")

    if not LOG_FILE.is_file():
        raise HTTPException(status_code=500, detail="logs/app.log is not a file")

    return PlainTextResponse(LOG_FILE.read_text(encoding="utf-8", errors="replace"))
