"""
LIMKOKWING LIBRARY MANAGEMENT SYSTEM
Student Name: Kadijatu Barrie
Student ID: 4226
Date: May 2026
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import asyncio

app = FastAPI(title="Limkokwing Library API")

# ---------- Models ----------
class Book(BaseModel):
    id: int
    title: str
    author: str
    category: str
    available: bool = True
    borrowed_by: Optional[int] = None
    due_date: Optional[str] = None

class BorrowRequest(BaseModel):
    user_id: int
    book_id: int

class ReturnRequest(BaseModel):
    user_id: int
    book_id: int

# ---------- Database ----------
books_db = {
    1: {"id": 1, "title": "Clean Code", "author": "Robert Martin", "category": "Programming", "available": True},
    2: {"id": 2, "title": "Python Crash Course", "author": "Eric Matthes", "category": "Programming", "available": True},
    3: {"id": 3, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "category": "Fiction", "available": True},
    4: {"id": 4, "title": "Sapiens", "author": "Yuval Harari", "category": "History", "available": True},
}

borrowings = {}  # user_id -> list of book_ids with due dates

# ---------- Endpoints ----------
@app.get("/")
def home():
    return {"message": "Library API is running!", "endpoints": ["/books", "/borrow", "/return", "/users/{id}/fines"]}

@app.get("/books")
async def get_books(title: Optional[str] = None, author: Optional[str] = None, category: Optional[str] = None):
    results = list(books_db.values())
    
    if title:
        results = [b for b in results if title.lower() in b["title"].lower()]
    if author:
        results = [b for b in results if author.lower() in b["author"].lower()]
    if category:
        results = [b for b in results if category.lower() == b["category"].lower()]
    
    return results

@app.post("/borrow")
async def borrow_book(request: BorrowRequest):
    book_id = request.book_id
    user_id = request.user_id
    
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")
    
    if not books_db[book_id]["available"]:
        raise HTTPException(status_code=400, detail="Book is not available")
    
    # Borrow the book
    books_db[book_id]["available"] = False
    due_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    
    if user_id not in borrowings:
        borrowings[user_id] = []
    
    borrowings[user_id].append({
        "book_id": book_id,
        "title": books_db[book_id]["title"],
        "due_date": due_date
    })
    
    return {"message": f"Book '{books_db[book_id]['title']}' borrowed successfully", "due_date": due_date}

@app.post("/return")
async def return_book(request: ReturnRequest):
    book_id = request.book_id
    user_id = request.user_id
    
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")
    
    if books_db[book_id]["available"]:
        raise HTTPException(status_code=400, detail="Book is not borrowed")
    
    # Calculate fine if overdue
    fine = 0
    if user_id in borrowings:
        for borrowing in borrowings[user_id]:
            if borrowing["book_id"] == book_id:
                due_date = datetime.strptime(borrowing["due_date"], "%Y-%m-%d")
                if datetime.now() > due_date:
                    days_overdue = (datetime.now() - due_date).days
                    fine = days_overdue * 0.50
                break
    
    # Return the book
    books_db[book_id]["available"] = True
    
    # Remove from borrowings
    if user_id in borrowings:
        borrowings[user_id] = [b for b in borrowings[user_id] if b["book_id"] != book_id]
    
    return {"message": "Book returned successfully", "fine": fine}

@app.get("/users/{user_id}/fines")
async def get_fines(user_id: int):
    if user_id not in borrowings or not borrowings[user_id]:
        return {"user_id": user_id, "overdue_books": [], "total_fine": 0}
    
    overdue_books = []
    total_fine = 0
    
    for borrowing in borrowings[user_id]:
        due_date = datetime.strptime(borrowing["due_date"], "%Y-%m-%d")
        if datetime.now() > due_date:
            days_overdue = (datetime.now() - due_date).days
            fine = days_overdue * 0.50
            total_fine += fine
            overdue_books.append({
                "book_id": borrowing["book_id"],
                "title": borrowing["title"],
                "due_date": borrowing["due_date"],
                "fine": fine
            })
    
    return {"user_id": user_id, "overdue_books": overdue_books, "total_fine": total_fine}

