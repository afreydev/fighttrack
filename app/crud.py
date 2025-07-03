# app/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, extract
from datetime import datetime, timedelta
from typing import List, Optional
from app import models, schemas

# Student CRUD
def get_student(db: Session, student_id: int):
    return db.query(models.Student).filter(models.Student.id == student_id).first()

def get_student_by_document(db: Session, document: str):
    return db.query(models.Student).filter(models.Student.document == document).first()

def get_students(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Student).offset(skip).limit(limit).all()

def create_student(db: Session, student: schemas.StudentCreate):
    db_student = models.Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def update_student(db: Session, student_id: int, student: schemas.StudentUpdate):
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if db_student:
        for key, value in student.dict(exclude_unset=True).items():
            setattr(db_student, key, value)
        db_student.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_student)
    return db_student

def delete_student(db: Session, student_id: int):
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if db_student:
        db.delete(db_student)
        db.commit()
    return db_student

# Plan CRUD
def get_plan(db: Session, plan_id: int):
    return db.query(models.Plan).filter(models.Plan.id == plan_id).first()

def get_plans(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Plan).offset(skip).limit(limit).all()

def create_plan(db: Session, plan: schemas.PlanCreate):
    db_plan = models.Plan(**plan.dict())
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

def update_plan(db: Session, plan_id: int, plan: schemas.PlanUpdate):
    db_plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if db_plan:
        for key, value in plan.dict(exclude_unset=True).items():
            setattr(db_plan, key, value)
        db_plan.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_plan)
    return db_plan

def delete_plan(db: Session, plan_id: int):
    db_plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if db_plan:
        db.delete(db_plan)
        db.commit()
    return db_plan

# StudentPlan CRUD
def get_student_plan(db: Session, student_plan_id: int):
    return db.query(models.StudentPlan).filter(models.StudentPlan.id == student_plan_id).first()

def get_student_plans(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.StudentPlan).offset(skip).limit(limit).all()

def get_active_student_plan(db: Session, student_id: int):
    return db.query(models.StudentPlan).filter(
        and_(
            models.StudentPlan.student_id == student_id,
            models.StudentPlan.is_active == True,
            models.StudentPlan.start_date <= datetime.utcnow(),
            models.StudentPlan.end_date >= datetime.utcnow()
        )
    ).first()

def create_student_plan(db: Session, student_plan: schemas.StudentPlanCreate):
    db_student_plan = models.StudentPlan(**student_plan.dict())
    db.add(db_student_plan)
    db.commit()
    db.refresh(db_student_plan)
    return db_student_plan

def update_student_plan(db: Session, student_plan_id: int, student_plan: schemas.StudentPlanUpdate):
    db_student_plan = db.query(models.StudentPlan).filter(models.StudentPlan.id == student_plan_id).first()
    if db_student_plan:
        for key, value in student_plan.dict(exclude_unset=True).items():
            setattr(db_student_plan, key, value)
        db_student_plan.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_student_plan)
    return db_student_plan

def delete_student_plan(db: Session, student_plan_id: int):
    db_student_plan = db.query(models.StudentPlan).filter(models.StudentPlan.id == student_plan_id).first()
    if db_student_plan:
        db.delete(db_student_plan)
        db.commit()
    return db_student_plan

# AccessLog CRUD
def get_access_log(db: Session, access_log_id: int):
    return db.query(models.AccessLog).filter(models.AccessLog.id == access_log_id).first()

def get_access_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.AccessLog).offset(skip).limit(limit).all()

def create_access_log(db: Session, access_log: schemas.AccessLogCreate):
    db_access_log = models.AccessLog(**access_log.dict())
    db.add(db_access_log)
    db.commit()
    db.refresh(db_access_log)
    return db_access_log

def get_monthly_access_count(db: Session, student_plan_id: int, month: int, year: int):
    return db.query(models.AccessLog).filter(
        and_(
            models.AccessLog.student_plan_id == student_plan_id,
            extract('month', models.AccessLog.access_time) == month,
            extract('year', models.AccessLog.access_time) == year
        )
    ).count()

def can_student_access(db: Session, student_id: int) -> tuple[bool, str, Optional[models.StudentPlan]]:
    """Check if student can access based on their active plan"""
    student_plan = get_active_student_plan(db, student_id)
    
    if not student_plan:
        return False, "No hay plan activo para este estudiante", None
    
    # Check if current date is within plan period
    now = datetime.utcnow()
    if now < student_plan.start_date or now > student_plan.end_date:
        return False, "El plan no está activo en este período", student_plan
    
    # Count accesses this month
    current_month = now.month
    current_year = now.year
    monthly_accesses = get_monthly_access_count(db, student_plan.id, current_month, current_year)
    
    if monthly_accesses >= student_plan.plan.monthly_entries:
        return False, "Has agotado tu límite mensual de ingresos", student_plan
    
    return True, "Acceso permitido", student_plan

def get_student_report(db: Session, student_id: int):
    student = get_student(db, student_id)
    if not student:
        return None
    
    current_plan = get_active_student_plan(db, student_id)
    access_logs = db.query(models.AccessLog).filter(models.AccessLog.student_id == student_id).all()
    
    total_accesses = len(access_logs)
    remaining_accesses = 0
    
    if current_plan:
        now = datetime.utcnow()
        monthly_accesses = get_monthly_access_count(db, current_plan.id, now.month, now.year)
        remaining_accesses = max(0, current_plan.plan.monthly_entries - monthly_accesses)
    
    # Convert current_plan to dict format for easier handling
    current_plan_data = None
    if current_plan:
        current_plan_data = {
            "id": current_plan.id,
            "student_id": current_plan.student_id,
            "plan_id": current_plan.plan_id,
            "start_date": current_plan.start_date,
            "end_date": current_plan.end_date,
            "is_active": current_plan.is_active,
            "created_at": current_plan.created_at,
            "updated_at": current_plan.updated_at,
            "plan": {
                "id": current_plan.plan.id,
                "name": current_plan.plan.name,
                "monthly_entries": current_plan.plan.monthly_entries,
                "created_at": current_plan.plan.created_at,
                "updated_at": current_plan.plan.updated_at
            } if current_plan.plan else None
        }
    
    # Convert access_logs to dict format
    access_logs_data = []
    for log in access_logs:
        access_logs_data.append({
            "id": log.id,
            "student_id": log.student_id,
            "student_plan_id": log.student_plan_id,
            "access_time": log.access_time,
            "notes": log.notes,
            "student_plan": {
                "id": log.student_plan.id,
                "plan": {
                    "id": log.student_plan.plan.id,
                    "name": log.student_plan.plan.name,
                    "monthly_entries": log.student_plan.plan.monthly_entries
                } if log.student_plan.plan else None
            } if log.student_plan else None
        })
    
    return {
        "student": {
            "id": student.id,
            "name": student.name,
            "document": student.document,
            "created_at": student.created_at,
            "updated_at": student.updated_at
        },
        "current_plan": current_plan_data,
        "total_accesses": total_accesses,
        "remaining_accesses": remaining_accesses,
        "access_logs": access_logs_data
    }

def get_plan_report(db: Session, plan_id: int):
    plan = get_plan(db, plan_id)
    if not plan:
        return None
    
    # Get active students with this plan
    active_students = db.query(models.StudentPlan).filter(
        and_(
            models.StudentPlan.plan_id == plan_id,
            models.StudentPlan.is_active == True,
            models.StudentPlan.start_date <= datetime.utcnow(),
            models.StudentPlan.end_date >= datetime.utcnow()
        )
    ).count()
    
    # Get total accesses for this plan
    total_accesses = db.query(models.AccessLog).join(models.StudentPlan).filter(
        models.StudentPlan.plan_id == plan_id
    ).count()
    
    # Get students with this plan (with full relationship data)
    students_with_plan = db.query(models.StudentPlan).filter(
        models.StudentPlan.plan_id == plan_id
    ).all()
    
    # Convert to dict format for easier handling
    students_with_plan_data = []
    for sp in students_with_plan:
        # Count monthly accesses for this student plan
        now = datetime.utcnow()
        monthly_accesses = get_monthly_access_count(db, sp.id, now.month, now.year)
        
        students_with_plan_data.append({
            "id": sp.id,
            "student_id": sp.student_id,
            "plan_id": sp.plan_id,
            "start_date": sp.start_date,
            "end_date": sp.end_date,
            "is_active": sp.is_active,
            "monthly_accesses": monthly_accesses,
            "student": {
                "id": sp.student.id,
                "name": sp.student.name,
                "document": sp.student.document,
                "created_at": sp.student.created_at,
                "updated_at": sp.student.updated_at
            } if sp.student else None,
            "plan": {
                "id": sp.plan.id,
                "name": sp.plan.name,
                "monthly_entries": sp.plan.monthly_entries,
                "created_at": sp.plan.created_at,
                "updated_at": sp.plan.updated_at
            } if sp.plan else None
        })
    
    return {
        "plan": {
            "id": plan.id,
            "name": plan.name,
            "monthly_entries": plan.monthly_entries,
            "created_at": plan.created_at,
            "updated_at": plan.updated_at
        },
        "active_students": active_students,
        "total_accesses": total_accesses,
        "students_with_plan": students_with_plan_data
    }
