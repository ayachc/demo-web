from fastapi import APIRouter

from app.services.inventory import decrease_stock


router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("")
def create_order(book_id: int):
    stock = decrease_stock(book_id)
    return {"book_id": book_id, "status": "paid", "remaining_stock": stock}
