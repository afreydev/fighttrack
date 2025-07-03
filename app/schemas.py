# app/schemas.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# Student schemas
class StudentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    document: str = Field(..., min_length=1, max_length=50)

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    document: Optional[str] = Field(None, min_length=1, max_length=50)

class Student(StudentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Plan schemas
class PlanBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    monthly_entries: int = Field(..., ge=1)

class PlanCreate(PlanBase):
    pass

class PlanUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    monthly_entries: Optional[int] = Field(None, ge=1)

class Plan(PlanBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# StudentPlan schemas
class StudentPlanBase(BaseModel):
    student_id: int
    plan_id: int
    start_date: datetime
    end_date: datetime
    is_active: bool = True

class StudentPlanCreate(StudentPlanBase):
    pass

class StudentPlanUpdate(BaseModel):
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None

class StudentPlan(StudentPlanBase):
    id: int
    created_at: datetime
    updated_at: datetime
    student: Student
    plan: Plan
    
    class Config:
        from_attributes = True

# AccessLog schemas
class AccessLogBase(BaseModel):
    student_id: int
    student_plan_id: int
    notes: Optional[str] = None

class AccessLogCreate(AccessLogBase):
    pass

class AccessLog(AccessLogBase):
    id: int
    access_time: datetime
    student: Student
    student_plan: StudentPlan
    
    class Config:
        from_attributes = True

# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class StudentAccess(BaseModel):
    document: str

# Report schemas
class StudentReport(BaseModel):
    student: Student
    current_plan: Optional[StudentPlan] = None
    total_accesses: int
    remaining_accesses: int
    access_logs: List[AccessLog]

class PlanReport(BaseModel):
    plan: Plan
    active_students: int
    total_accesses: int
    students_with_plan: List[dict]
