import contextvars
import logging
import time
import uuid
from logging.handlers import RotatingFileHandler
from pathlib import Path

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

LOG_DIR = Path("logs")
request_id_context: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id",
    default="-",
)


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_context.get()
        return True


def configure_logging() -> None:
    LOG_DIR.mkdir(exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] [request_id=%(request_id)s] %(message)s"
    )
    request_filter = RequestIdFilter()

    app_handler = RotatingFileHandler(
        LOG_DIR / "app.log",
        maxBytes=2_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    app_handler.setFormatter(formatter)
    app_handler.addFilter(request_filter)

    error_handler = RotatingFileHandler(
        LOG_DIR / "error.log",
        maxBytes=2_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    error_handler.addFilter(request_filter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.addFilter(request_filter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)

    access_logger = logging.getLogger("asset_service.access")
    access_logger.propagate = False
    access_logger.setLevel(logging.INFO)
    access_logger.handlers.clear()

    access_handler = RotatingFileHandler(
        LOG_DIR / "access.log",
        maxBytes=2_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    access_handler.setFormatter(formatter)
    access_handler.addFilter(request_filter)
    access_logger.addHandler(access_handler)
    access_logger.addHandler(console_handler)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = request_id_context.set(request_id)
        started_at = time.perf_counter()
        access_logger = logging.getLogger("asset_service.access")
        error_logger = logging.getLogger("asset_service.error")

        try:
            response = await call_next(request)
        except Exception:
            elapsed_ms = (time.perf_counter() - started_at) * 1000
            error_logger.exception(
                "Unhandled request error method=%s path=%s client=%s elapsed_ms=%.2f",
                request.method,
                request.url.path,
                request.client.host if request.client else "-",
                elapsed_ms,
            )
            request_id_context.reset(token)
            raise

        elapsed_ms = (time.perf_counter() - started_at) * 1000
        response.headers["X-Request-ID"] = request_id
        access_logger.info(
            "method=%s path=%s status=%s client=%s elapsed_ms=%.2f",
            request.method,
            request.url.path,
            response.status_code,
            request.client.host if request.client else "-",
            elapsed_ms,
        )
        request_id_context.reset(token)
        return response
