from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from models import ExpenseCategory


class ExpenseBase(BaseModel):
    amount: float = Field(..., gt=0, description="Amount must be positive")
    category: ExpenseCategory
    description: str = Field(..., min_length=1, max_length=255)
    date: Optional[datetime] = None


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0, description="Amount must be positive")
    category: Optional[ExpenseCategory] = None
    description: Optional[str] = Field(None, min_length=1, max_length=255)
    date: Optional[datetime] = None


class ExpenseResponse(ExpenseBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        orm_mode = True


class ExpenseFilter(BaseModel):
    category: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class ExpenseTotalResponse(BaseModel):
    total_amount: float
    category_breakdown: dict
    total_count: int 