# app/routers/reports.py
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app import crud

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

@router.get("/student/{student_id}")
def get_student_report(student_id: int, db: Session = Depends(get_db), authorized: bool = Depends(verify_admin_api)):
    report = crud.get_student_report(db, student_id)
    if not report:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return report

@router.get("/plan/{plan_id}")
def get_plan_report(plan_id: int, db: Session = Depends(get_db), authorized: bool = Depends(verify_admin_api)):
    report = crud.get_plan_report(db, plan_id)
    if not report:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    return report