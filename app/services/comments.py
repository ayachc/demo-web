import requests

from app.core.config import settings
from app.core.logger import get_logger


logger = get_logger(__name__)


def fetch_comments(book_id: int):
    try:
        response = requests.get(
            settings.COMMENT_API_URL,
            params={"book_id": book_id},
            timeout=1,
        )
        response.raise_for_status()
        return response.json()
    except requests.Timeout:
        logger.error(
            "ERROR: Comment API request timed out",
            exc_info=True,
            extra={"context": f"book_id={book_id}, url={settings.COMMENT_API_URL}"},
        )
        raise
    except requests.RequestException:
        logger.error(
            "ERROR: Comment API request failed",
            exc_info=True,
            extra={"context": f"book_id={book_id}, url={settings.COMMENT_API_URL}"},
        )
        raise
