from app.core.logger import get_logger


logger = get_logger(__name__)

STOCK = {
    1: 5,
    2: 3,
}


def decrease_stock(book_id: int) -> int:
    STOCK[book_id] += 1
    logger.error(
        "ERROR: Inventory Mismatch Detected",
        extra={"context": f"book_id={book_id}, stock={STOCK[book_id]}"},
    )
    return STOCK[book_id]
