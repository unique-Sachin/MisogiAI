from sqlalchemy.orm import Session
from sqlalchemy import and_
from models import Expense, ExpenseCategory
from schemas import ExpenseCreate, ExpenseUpdate
from datetime import datetime, date
from typing import List, Optional
from collections import defaultdict


def get_expenses(db: Session, skip: int = 0, limit: int = 100, 
                start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Expense]:
    """Get all expenses with optional date filtering"""
    query = db.query(Expense)
    
    if start_date:
        query = query.filter(Expense.date >= start_date)
    if end_date:
        query = query.filter(Expense.date <= end_date)
    
    return query.offset(skip).limit(limit).all()


def get_expense(db: Session, expense_id: int) -> Optional[Expense]:
    """Get a single expense by ID"""
    return db.query(Expense).filter(Expense.id == expense_id).first()


def create_expense(db: Session, expense: ExpenseCreate) -> Expense:
    """Create a new expense"""
    db_expense = Expense(
        amount=expense.amount,
        category=expense.category,
        description=expense.description,
        date=expense.date or datetime.now()
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def update_expense(db: Session, expense_id: int, expense_update: ExpenseUpdate) -> Optional[Expense]:
    """Update an existing expense"""
    db_expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not db_expense:
        return None
    
    update_data = expense_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_expense, field, value)
    
    db.commit()
    db.refresh(db_expense)
    return db_expense


def delete_expense(db: Session, expense_id: int) -> bool:
    """Delete an expense"""
    db_expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not db_expense:
        return False
    
    db.delete(db_expense)
    db.commit()
    return True


def get_expenses_by_category(db: Session, category: str) -> List[Expense]:
    """Get expenses filtered by category"""
    try:
        expense_category = ExpenseCategory(category)
        return db.query(Expense).filter(Expense.category == expense_category).all()
    except ValueError:
        return []


def get_expenses_total(db: Session, start_date: Optional[date] = None, 
                      end_date: Optional[date] = None) -> dict:
    """Get total expenses and breakdown by category"""
    query = db.query(Expense)
    
    if start_date:
        query = query.filter(Expense.date >= start_date)
    if end_date:
        query = query.filter(Expense.date <= end_date)
    
    expenses = query.all()
    
    total_amount = sum(expense.amount for expense in expenses)
    category_breakdown = defaultdict(float)
    
    for expense in expenses:
        category_breakdown[expense.category.value] += expense.amount
    
    return {
        "total_amount": total_amount,
        "category_breakdown": dict(category_breakdown),
        "total_count": len(expenses)
    }


def create_sample_data(db: Session):
    """Create sample data for testing"""
    sample_expenses = [
        {"amount": 25.50, "category": ExpenseCategory.FOOD, "description": "Lunch at restaurant"},
        {"amount": 12.00, "category": ExpenseCategory.TRANSPORT, "description": "Bus fare"},
        {"amount": 150.00, "category": ExpenseCategory.UTILITIES, "description": "Electric bill"},
        {"amount": 30.00, "category": ExpenseCategory.ENTERTAINMENT, "description": "Movie tickets"},
        {"amount": 80.00, "category": ExpenseCategory.SHOPPING, "description": "Clothes shopping"},
        {"amount": 45.75, "category": ExpenseCategory.HEALTHCARE, "description": "Pharmacy"},
        {"amount": 200.00, "category": ExpenseCategory.EDUCATION, "description": "Online course"},
        {"amount": 15.25, "category": ExpenseCategory.OTHER, "description": "Miscellaneous"},
    ]
    
    for expense_data in sample_expenses:
        db_expense = Expense(**expense_data)
        db.add(db_expense)
    
    db.commit() 