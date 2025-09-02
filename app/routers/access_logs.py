# app/routers/access_logs.py
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

@router.get("/", response_model=List[schemas.AccessLog])
def read_access_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), authorized: bool = Depends(verify_admin_api)):
    access_logs = crud.get_access_logs(db, skip=skip, limit=limit)
    return access_logs

@router.post("/", response_model=schemas.AccessLog)
def create_access_log(access_log: schemas.AccessLogCreate, db: Session = Depends(get_db), authorized: bool = Depends(verify_admin_api)):
    # Verify student exists
    student = crud.get_student(db, access_log.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    try:
        return crud.create_access_log(db=db, access_log=access_log)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{access_log_id}", response_model=schemas.AccessLog)
def read_access_log(access_log_id: int, db: Session = Depends(get_db), authorized: bool = Depends(verify_admin_api)):
    db_access_log = crud.get_access_log(db, access_log_id=access_log_id)
    if db_access_log is None:
        raise HTTPException(status_code=404, detail="Registro de acceso no encontrado")
    return db_access_log

@router.post("/student-access")
def student_access(student_access: schemas.StudentAccess, db: Session = Depends(get_db)):
    student = crud.get_student_by_document(db, student_access.document)
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    can_access, message, student_plan = crud.can_student_access(db, student.id)
    
    if not can_access:
        raise HTTPException(status_code=403, detail=message)
    
    # Create access log
    access_log_data = schemas.AccessLogCreate(
        student_id=student.id,
        student_plan_id=student_plan.id,
        notes="Acceso registrado automáticamente"
    )
    
    access_log = crud.create_access_log(db, access_log_data)
    
    return {
        "message": f"¡Bienvenido {student.name}! Acceso permitido.",
        "student": student,
        "plan": student_plan.plan,
        "access_log": access_log
    }