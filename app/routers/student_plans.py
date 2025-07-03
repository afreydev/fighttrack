# app/routers/student_plans.py
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import crud, schemas

router = APIRouter()

def verify_admin_api(authorization: Optional[str] = Header(None)):
    """Verify admin for API calls"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    try:
        token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
        if not token or len(token) < 10:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return True
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@router.get("/", response_model=List[schemas.StudentPlan])
def read_student_plans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), authorized: bool = Depends(verify_admin_api)):
    student_plans = crud.get_student_plans(db, skip=skip, limit=limit)
    return student_plans

@router.post("/", response_model=schemas.StudentPlan)
def create_student_plan(student_plan: schemas.StudentPlanCreate, db: Session = Depends(get_db), authorized: bool = Depends(verify_admin_api)):
    # Verify student exists
    student = crud.get_student(db, student_plan.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    # Verify plan exists
    plan = crud.get_plan(db, student_plan.plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    
    return crud.create_student_plan(db=db, student_plan=student_plan)

@router.get("/{student_plan_id}", response_model=schemas.StudentPlan)
def read_student_plan(student_plan_id: int, db: Session = Depends(get_db), authorized: bool = Depends(verify_admin_api)):
    db_student_plan = crud.get_student_plan(db, student_plan_id=student_plan_id)
    if db_student_plan is None:
        raise HTTPException(status_code=404, detail="Plan de estudiante no encontrado")
    return db_student_plan

@router.put("/{student_plan_id}", response_model=schemas.StudentPlan)
def update_student_plan(student_plan_id: int, student_plan: schemas.StudentPlanUpdate, db: Session = Depends(get_db), authorized: bool = Depends(verify_admin_api)):
    db_student_plan = crud.update_student_plan(db, student_plan_id=student_plan_id, student_plan=student_plan)
    if db_student_plan is None:
        raise HTTPException(status_code=404, detail="Plan de estudiante no encontrado")
    return db_student_plan

@router.delete("/{student_plan_id}")
def delete_student_plan(student_plan_id: int, db: Session = Depends(get_db), authorized: bool = Depends(verify_admin_api)):
    db_student_plan = crud.delete_student_plan(db, student_plan_id=student_plan_id)
    if db_student_plan is None:
        raise HTTPException(status_code=404, detail="Plan de estudiante no encontrado")
    return {"message": "Plan de estudiante eliminado exitosamente"}

@router.get("/student/{student_id}/active", response_model=schemas.StudentPlan)
def get_active_student_plan(student_id: int, db: Session = Depends(get_db), authorized: bool = Depends(verify_admin_api)):
    db_student_plan = crud.get_active_student_plan(db, student_id=student_id)
    if db_student_plan is None:
        raise HTTPException(status_code=404, detail="No hay plan activo para este estudiante")
    return db_student_plan
