# Library API System

## Overview

This project is a REST API for managing library operations such as searching, borrowing, and returning books.

## Features

* Search books by title, author, category
* Borrow and return books
* Track overdue books
* Calculate fines
* View popular books

## Technologies

* Python
* FastAPI
* Uvicorn

## How to Run

1. Install dependencies:
   pip install -r requirements.txt

2. Start server:
   uvicorn main:app --reload

3. Open browser:
   http://127.0.0.1:8000/docs

## API Endpoints

* GET /catalogue
* POST /lend
* POST /receive
* GET /members/{id}/penalties
* GET /items/popular

## Author
kadijatu Barrie
4226
