# Sistema de Control de Acceso para Estudiantes

Un sistema web completo para gestionar el acceso de estudiantes a clases basado en planes mensuales.

## Características

- 📚 **Gestión de Estudiantes**: Registro completo con nombre, documento y timestamps
- 📋 **Planes Flexibles**: Definición de planes con número de ingresos mensuales
- 👥 **Asignación de Planes**: Vinculación de estudiantes a planes con fechas de vigencia
- 🚪 **Control de Acceso**: Validación automática de ingresos basada en planes activos
- 📊 **Reportes**: Informes detallados por estudiante y por plan
- 🔒 **Autenticación**: Sistema seguro para administradores y acceso simple para estudiantes
- 🐳 **Docker Ready**: Desplegado fácil con Docker Compose

## Tecnologías

- **Backend**: FastAPI con Python 3.11
- **Base de Datos**: PostgreSQL 15
- **ORM**: SQLAlchemy con Alembic para migraciones
- **Frontend**: HTML + Bootstrap 5 + JavaScript
- **Autenticación**: JWT tokens
- **Contenedores**: Docker & Docker Compose

## Instalación Rápida

### Prerequisitos
- Docker y Docker Compose instalados
- Git para clonar el repositorio

### Pasos de Instalación

1. **Clonar y crear la estructura del proyecto:**
```bash
mkdir access_control_system
cd access_control_system
```

2. **Crear todos los archivos según la estructura mostrada en los artefactos**

3. **Construir y ejecutar con Docker:**
```bash
docker-compose up --build
```

4. **Acceder al sistema:**
   - Aplicación: http://localhost:8000
   - Administrador: admin / admin123

## Estructura del Proyecto

```
access_control_system/
├── docker-compose.yml          # Configuración de contenedores
├── Dockerfile                  # Imagen de la aplicación
├── requirements.txt            # Dependencias Python
├── alembic.ini                # Configuración de migraciones
├── app/                       # Código de la aplicación
│   ├── main.py               # Aplicación principal FastAPI
│   ├── database.py           # Configuración de base de datos
│   ├── models.py             # Modelos SQLAlchemy
│   ├── schemas.py            # Esquemas Pydantic
│   ├── crud.py               # Operaciones de base de datos
│   ├── auth.py               # Autenticación y autorización
│   ├── config.py             # Configuración de la aplicación
│   └── routers/              # Rutas de la API
├── templates/                # Plantillas HTML
│   ├── base.html            # Plantilla base
│   ├── login.html           # Página de login
│   ├── admin/               # Páginas de administración
│   ├── student/             # Páginas de estudiantes
│   └── reports/             # Páginas de reportes
└── static/                  # Archivos estáticos (CSS, JS)
```

## Uso del Sistema

### Administrador

1. **Acceso**: http://localhost:8000/admin/login
   - Usuario: `admin`
   - Contraseña: `admin123`

2. **Funcionalidades**:
   - **Estudiantes**: Crear, editar, eliminar y buscar estudiantes
   - **Planes**: Definir planes con número de ingresos mensuales
   - **Asignación**: Vincular estudiantes a planes con fechas
   - **Registros**: Ver todos los accesos registrados
   - **Reportes**: Generar informes por estudiante o plan

### Estudiantes

1. **Acceso**: http://localhost:8000/student/access
2. **Proceso**:
   - Ingresar número de documento
   - El sistema valida automáticamente:
     - Existencia del estudiante
     - Plan activo vigente
     - Ingresos disponibles en el mes
   - Registra el acceso si todo es válido

## API Endpoints

### Autenticación
- `POST /api/admin/login` - Login de administrador
- `GET /api/admin/me` - Información del usuario actual

### Estudiantes
- `GET /api/students/` - Listar estudiantes
- `POST /api/students/` - Crear estudiante
- `GET /api/students/{id}` - Obtener estudiante
- `PUT /api/students/{id}` - Actualizar estudiante
- `DELETE /api/students/{id}` - Eliminar estudiante

### Planes
- `GET /api/plans/` - Listar planes
- `POST /api/plans/` - Crear plan
- `GET /api/plans/{id}` - Obtener plan
- `PUT /api/plans/{id}` - Actualizar plan
- `DELETE /api/plans/{id}` - Eliminar plan

### Asignación de Planes
- `GET /api/student-plans/` - Listar asignaciones
- `POST /api/student-plans/` - Crear asignación
- `GET /api/student-plans/{id}` - Obtener asignación
- `PUT /api/student-plans/{id}` - Actualizar asignación
- `DELETE /api/student-plans/{id}` - Eliminar asignación

### Registros de Acceso
- `GET /api/access-logs/` - Listar registros
- `POST /api/access-logs/` - Crear registro
- `POST /api/access-logs/student-access` - Acceso de estudiante

### Reportes
- `GET /api/reports/student/{id}` - Reporte de estudiante
- `GET /api/reports/plan/{id}` - Reporte de plan

## Configuración

### Variables de Entorno

```bash
DATABASE_URL=postgresql://admin:admin123@db:5432/access_control
SECRET_KEY=your-secret-key-change-this-in-production
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

### Base de Datos

El sistema usa PostgreSQL con las siguientes tablas:
- `students` - Información de estudiantes
- `plans` - Definición de planes
- `student_plans` - Asignación de planes a estudiantes
- `access_logs` - Registro de accesos
- `admins` - Usuarios administradores

## Desarrollo

### Ejecutar en modo desarrollo:
```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos
alembic upgrade head

# Ejecutar servidor
uvicorn app.main:app --reload
```

### Crear nueva migración:
```bash
alembic revision --autogenerate -m "descripción de cambios"
alembic upgrade head
```

## Seguridad

- Autenticación JWT para administradores
- Contraseñas hasheadas con bcrypt
- Validación de datos con Pydantic
- Protección CSRF en formularios
- Sanitización de entradas

## Producción

Para producción, asegúrate de:

1. Cambiar las credenciales por defecto
2. Usar una SECRET_KEY segura
3. Configurar HTTPS
4. Implementar backups de base de datos
5. Monitoreo y logs
6. Limitar acceso a puertos de base de datos

## Soporte

Este sistema está diseñado para ser simple pero robusto. Incluye:
- Manejo de errores completo
- Validaciones de integridad
- Interfaz intuitiva
- Documentación automática de API en `/docs`
- Logs detallados para debugging

## Licencia

Proyecto de código abierto para uso educativo y comercial.
