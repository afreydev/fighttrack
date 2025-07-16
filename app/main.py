# app/main.py
from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db, engine
from app.models import Base
from app.auth import authenticate_admin, create_access_token, get_current_admin, create_admin_user
from app.schemas import Token, UserLogin, StudentAccess, AccessLogCreate
from app.crud import get_student_by_document, can_student_access, create_access_log
from app.config import settings
from app.routers import admin, students, plans, student_plans, access_logs, reports
from app import schemas

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Control de Acceso")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(students.router, prefix="/api/students", tags=["students"])
app.include_router(plans.router, prefix="/api/plans", tags=["plans"])
app.include_router(student_plans.router, prefix="/api/student-plans", tags=["student-plans"])
app.include_router(access_logs.router, prefix="/api/access-logs", tags=["access-logs"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])

# Security
security = HTTPBearer()

@app.on_event("startup")
async def startup_event():
    """Create default admin user on startup"""
    db = next(get_db())
    try:
        create_admin_user(db)
    finally:
        db.close()

def verify_admin_session(request: Request):
    """Verify admin session from cookie for HTML pages"""
    token = request.cookies.get("access_token")
    if not token or not token.startswith("Bearer "):
        return None
    return token

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "admin": True})

@app.post("/admin/login")
async def admin_login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    print(f"=== DEBUG admin_login ===")
    print(f"Username: {username}")
    
    admin = authenticate_admin(db, username, password)
    if not admin:
        print("Authentication failed")
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "admin": True,
            "error": "Usuario o contraseña incorrectos"
        })
    
    print("Authentication successful")
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": admin.username}, expires_delta=access_token_expires
    )
    
    print(f"Generated token: {access_token[:20]}...")
    
    response = RedirectResponse(url="/admin/dashboard", status_code=302)
    cookie_value = f"Bearer {access_token}"
    print(f"Setting cookie value: {cookie_value[:30]}...")
    
    # Set cookie that JavaScript can read
    response.set_cookie(
        key="access_token", 
        value=cookie_value, 
        httponly=False,  # Changed to False so JavaScript can read it
        max_age=settings.access_token_expire_minutes * 60,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax"
    )
    
    print("Cookie set, redirecting to dashboard")
    return response

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    token = verify_admin_session(request)
    if not token:
        return RedirectResponse(url="/admin/login", status_code=302)
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})

@app.get("/admin/students", response_class=HTMLResponse)
async def admin_students(request: Request):
    token = verify_admin_session(request)
    if not token:
        return RedirectResponse(url="/admin/login", status_code=302)
    return templates.TemplateResponse("admin/students.html", {"request": request})

@app.get("/admin/plans", response_class=HTMLResponse)
async def admin_plans(request: Request):
    token = verify_admin_session(request)
    if not token:
        return RedirectResponse(url="/admin/login", status_code=302)
    return templates.TemplateResponse("admin/plans.html", {"request": request})

@app.get("/admin/student-plans", response_class=HTMLResponse)
async def admin_student_plans(request: Request):
    token = verify_admin_session(request)
    if not token:
        return RedirectResponse(url="/admin/login", status_code=302)
    return templates.TemplateResponse("admin/student_plans.html", {"request": request})

@app.get("/admin/access-logs", response_class=HTMLResponse)
async def admin_access_logs(request: Request):
    token = verify_admin_session(request)
    if not token:
        return RedirectResponse(url="/admin/login", status_code=302)
    return templates.TemplateResponse("admin/access_logs.html", {"request": request})

@app.get("/student/access", response_class=HTMLResponse)
async def student_access_page(request: Request):
    return templates.TemplateResponse("student/access.html", {"request": request})

@app.post("/student/access")
async def student_access(
    request: Request,
    document: str = Form(...),
    db: Session = Depends(get_db)
):
    student = get_student_by_document(db, document)
    if not student:
        return templates.TemplateResponse("student/access.html", {
            "request": request,
            "error": "Estudiante no encontrado"
        })
    
    can_access, message, student_plan, pending_monthly_accesses = can_student_access(db, student.id)
    
    if can_access:
        # Create access log using the proper schema
        access_log_data = schemas.AccessLogCreate(
            student_id=student.id,
            student_plan_id=student_plan.id,
            notes="Acceso registrado automáticamente"
        )
        create_access_log(db, access_log_data)
        
        return templates.TemplateResponse("student/access.html", {
            "request": request,
            "success": f"¡Bienvenido {student.name}! Acceso permitido.",
            "student": student,
            "plan": student_plan.plan if student_plan else None,
            "pending": pending_monthly_accesses
        })
    else:
        return templates.TemplateResponse("student/access.html", {
            "request": request,
            "error": message,
            "student": student
        })

@app.get("/reports/student/{student_id}", response_class=HTMLResponse)
async def student_report_page(request: Request, student_id: int):
    return templates.TemplateResponse("reports/student_report.html", {
        "request": request,
        "student_id": student_id
    })

@app.get("/reports/plan/{plan_id}", response_class=HTMLResponse)
async def plan_report_page(request: Request, plan_id: int):
    return templates.TemplateResponse("reports/plan_report.html", {
        "request": request,
        "plan_id": plan_id
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

@app.post("/debug/create-test-data")
async def create_test_data(db: Session = Depends(get_db)):
    """Create test data for debugging"""
    try:
        # Create test students
        test_students = [
            {"name": "Juan Pérez", "document": "12345678"},
            {"name": "María García", "document": "87654321"},
            {"name": "Carlos López", "document": "11223344"}
        ]
        
        created_students = []
        for student_data in test_students:
            existing = crud.get_student_by_document(db, student_data["document"])
            if not existing:
                student = crud.create_student(db, schemas.StudentCreate(**student_data))
                created_students.append(student)
        
        # Create test plans
        test_plans = [
            {"name": "Plan Básico", "monthly_entries": 8},
            {"name": "Plan Premium", "monthly_entries": 12},
            {"name": "Plan Ilimitado", "monthly_entries": 20}
        ]
        
        created_plans = []
        for plan_data in test_plans:
            plan = crud.create_plan(db, schemas.PlanCreate(**plan_data))
            created_plans.append(plan)
        
        # Create test student plans
        if created_students and created_plans:
            from datetime import datetime, timedelta
            
            start_date = datetime.now()
            end_date = start_date + timedelta(days=30)
            
            student_plan_data = schemas.StudentPlanCreate(
                student_id=created_students[0].id,
                plan_id=created_plans[0].id,
                start_date=start_date,
                end_date=end_date,
                is_active=True
            )
            
            student_plan = crud.create_student_plan(db, student_plan_data)
            
            # Create test access log
            access_log_data = schemas.AccessLogCreate(
                student_id=created_students[0].id,
                student_plan_id=student_plan.id,
                notes="Acceso de prueba"
            )
            
            crud.create_access_log(db, access_log_data)
        
        return {
            "message": "Test data created successfully",
            "students": len(created_students),
            "plans": len(created_plans)
        }
    
    except Exception as e:
        print(f"Error creating test data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(key="access_token")
    return response
