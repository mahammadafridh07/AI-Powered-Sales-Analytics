from datetime import date, datetime
from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, Field


# ---------------------------- Auth ----------------------------
class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------------------------- Filters ----------------------------
class DashboardFilters(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    region: Optional[str] = None
    category: Optional[str] = None
    product_id: Optional[int] = None
    segment: Optional[str] = None


# ---------------------------- Upload ----------------------------
class UploadStatus(BaseModel):
    job_id: int
    status: str
    rows_processed: int
    error_message: Optional[str] = None


# ---------------------------- AI ----------------------------
class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


class ChatResponse(BaseModel):
    answer: str
    data: Optional[Any] = None
    ai_configured: bool
