# app/routers/students.py
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.auth import verify_token_from_header
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
        # Remove 'Bearer ' prefix if present
        token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
        # For now, just check if token exists and is not empty
        # In production, you'd validate the JWT token properly
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

@router.get("/", response_model=List[schemas.Student])
def read_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), authorized: bool = Depends(verify_admin_api)):
    students = crud.get_students(db, skip=skip, limit=limit)
    return students

@router.post("/", response_model=schemas.Student)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db), authorized: bool = Depends(verify_admin_api)):
    db_student = crud.get_student_by_document(db, document=student.document)
    if db_student:
        raise HTTPException(status_code=400, detail="El documento ya está registrado")
    return crud.create_student(db=db, student=student)

@router.get("/{student_id}", response_model=schemas.Student)
def read_student(student_id: int, db: Session = Depends(get_db), authorized: bool = Depends(verify_admin_api)):
    db_student = crud.get_student(db, student_id=student_id)
    if db_student is None:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return db_student

@router.put("/{student_id}", response_model=schemas.Student)
def update_student(student_id: int, student: schemas.StudentUpdate, db: Session = Depends(get_db), authorized: bool = Depends(verify_admin_api)):
    db_student = crud.update_student(db, student_id=student_id, student=student)
    if db_student is None:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return db_student

@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db), authorized: bool = Depends(verify_admin_api)):
    db_student = crud.delete_student(db, student_id=student_id)
    if db_student is None:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return {"message": "Estudiante eliminado exitosamente"}

@router.get("/document/{document}", response_model=schemas.Student)
def read_student_by_document(document: str, db: Session = Depends(get_db)):
    db_student = crud.get_student_by_document(db, document=document)
    if db_student is None:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return db_student