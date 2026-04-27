from fastapi import APIRouter

from app.services.comments import fetch_comments
from app.services.report import export_books_report


router = APIRouter(prefix="/books", tags=["books"])

BOOKS = {
    1: {"id": 1, "title": "Clean Architecture", "price": 45.0},
    2: {"id": 2, "title": "Domain-Driven Design", "price": 59.0},
}


@router.get("")
def list_books():
    return list(BOOKS.values())


@router.get("/report")
def books_report():
    return {"csv": export_books_report(BOOKS)}


@router.get("/{book_id}")
def get_book(book_id: int):
    book = BOOKS[book_id]
    return {**book, "comments": fetch_comments(book_id)}
