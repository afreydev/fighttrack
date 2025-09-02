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
    """
    Get the truly active plan for a student
    Priority: is_active=True AND current date within range
    """
    now = datetime.utcnow()
    
    # First try: get plan that is both marked active AND within date range
    active_plan = db.query(models.StudentPlan).filter(
        and_(
            models.StudentPlan.student_id == student_id,
            models.StudentPlan.is_active == True,
            models.StudentPlan.start_date <= now,
            models.StudentPlan.end_date >= now
        )
    ).order_by(models.StudentPlan.created_at.desc()).first()
    
    if active_plan:
        return active_plan
    
    # If no active plan found, check if there are plans marked active but with wrong dates
    # This helps identify data inconsistencies
    marked_active = db.query(models.StudentPlan).filter(
        and_(
            models.StudentPlan.student_id == student_id,
            models.StudentPlan.is_active == True
        )
    ).all()
    
    # If we have plans marked as active but outside date range, fix them
    if marked_active:
        for plan in marked_active:
            if plan.end_date < now:
                plan.is_active = False
                plan.updated_at = now
        db.commit()
    
    return None

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
    # Get the student's active plan - ignore the student_plan_id from the request
    active_plan = get_active_student_plan(db, access_log.student_id)
    
    if not active_plan:
        raise ValueError("No hay plan activo para este estudiante")
    
    # Check if access is allowed
    can_access, message, _, remaining = can_student_access(db, access_log.student_id)
    if not can_access:
        raise ValueError(f"Acceso denegado: {message}")
    
    # Create access log with the CORRECT active plan (ignore request's student_plan_id)
    access_log_data = {
        "student_id": access_log.student_id,
        "student_plan_id": active_plan.id,  # Always use the active plan
        "notes": access_log.notes
    }
    
    db_access_log = models.AccessLog(**access_log_data)
    db.add(db_access_log)
    db.commit()
    db.refresh(db_access_log)

def get_monthly_access_count(db: Session, student_plan_id: int, month: int, year: int):
    return db.query(models.AccessLog).filter(
        and_(
            models.AccessLog.student_plan_id == student_plan_id,
            extract('month', models.AccessLog.access_time) == month,
            extract('year', models.AccessLog.access_time) == year
        )
    ).count()

def can_student_access(db: Session, student_id: int) -> tuple[bool, str, Optional[models.StudentPlan], Optional[int]]:
    """Check if student can access based on their active plan"""
    
    # Get the active plan - this should be the ONLY plan we check
    student_plan = get_active_student_plan(db, student_id)
    
    if not student_plan:
        return False, "No hay plan activo para este estudiante", None, 0
    
    # Double-check dates (should be redundant with improved get_active_student_plan)
    now = datetime.utcnow()
    if now < student_plan.start_date or now > student_plan.end_date:
        # This shouldn't happen with the improved function above
        # But if it does, deactivate the plan
        student_plan.is_active = False
        student_plan.updated_at = now
        db.commit()
        return False, "El plan ha expirado", None, 0
    
    # Count accesses this month for THIS specific plan
    current_month = now.month
    current_year = now.year
    monthly_accesses = get_monthly_access_count(db, student_plan.id, current_month, current_year)
    
    if monthly_accesses >= student_plan.plan.monthly_entries:
        return False, "Has agotado tu límite mensual de ingresos", student_plan, 0
    
    pending_monthly_accesses = student_plan.plan.monthly_entries - monthly_accesses
    
    return True, "Acceso permitido", student_plan, pending_monthly_accesses

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
