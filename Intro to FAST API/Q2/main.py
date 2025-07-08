from fastapi import FastAPI, Depends, HTTPException, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List, Optional
import crud
import models
import schemas
from database import SessionLocal, engine, get_db
from models import ExpenseCategory

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="Expense Tracker", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")


# Initialize sample data
@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    try:
        # Check if we have any expenses
        expenses = crud.get_expenses(db, limit=1)
        if not expenses:
            crud.create_sample_data(db)
    finally:
        db.close()


# Web UI Routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    expenses = crud.get_expenses(db)
    total_data = crud.get_expenses_total(db)
    categories = [category.value for category in ExpenseCategory]
    return templates.TemplateResponse("index.html", {
        "request": request,
        "expenses": expenses,
        "total_data": total_data,
        "categories": categories
    })


@app.post("/add-expense", response_class=HTMLResponse)
async def add_expense_form(
    request: Request,
    amount: float = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        expense_category = ExpenseCategory(category)
        expense_data = schemas.ExpenseCreate(
            amount=amount,
            category=expense_category,
            description=description
        )
        crud.create_expense(db, expense_data)
        return RedirectResponse(url="/", status_code=303)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid category")


# API Routes
@app.get("/expenses", response_model=List[schemas.ExpenseResponse])
def get_expenses(
    skip: int = Query(0),
    limit: int = Query(100),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all expenses with optional date filtering"""
    start_date_obj = None
    end_date_obj = None
    
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
    
    expenses = crud.get_expenses(db, skip=skip, limit=limit, 
                               start_date=start_date_obj, end_date=end_date_obj)
    return expenses


@app.post("/expenses", response_model=schemas.ExpenseResponse)
def create_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    """Create a new expense"""
    return crud.create_expense(db=db, expense=expense)


@app.put("/expenses/{expense_id}", response_model=schemas.ExpenseResponse)
def update_expense(
    expense_id: int,
    expense: schemas.ExpenseUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing expense"""
    db_expense = crud.update_expense(db, expense_id, expense)
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return db_expense


@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    """Delete an expense"""
    success = crud.delete_expense(db, expense_id)
    if not success:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted successfully"}


@app.get("/expenses/category/{category}", response_model=List[schemas.ExpenseResponse])
def get_expenses_by_category(category: str, db: Session = Depends(get_db)):
    """Filter expenses by category"""
    expenses = crud.get_expenses_by_category(db, category)
    if not expenses and category not in [cat.value for cat in ExpenseCategory]:
        raise HTTPException(status_code=400, detail="Invalid category")
    return expenses


@app.get("/expenses/total", response_model=schemas.ExpenseTotalResponse)
def get_expenses_total(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get total expenses and breakdown by category"""
    start_date_obj = None
    end_date_obj = None
    
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
    
    return crud.get_expenses_total(db, start_date_obj, end_date_obj)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 