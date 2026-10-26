from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.pets.pets_service import pets_service
from app.students.students_schemas import (
    CreateStudentDto,
    Student,
    StudentList,
    UpdateStudentDto,
)
from app.students.students_repository import students_repository

router = APIRouter(prefix="/api/students", tags=["Students"])

@router.get("", response_model=StudentList, summary="Obtener todos los estudiantes")
def find_all(
    limit: int = Query(default=100, ge=1, le=500, description="Límite de registros"),
    offset: int = Query(default=0, ge=0, description="Desplazamiento para paginación"),
    db: Session = Depends(get_db)
):
    """
    Recupera todos los registros de estudiantes almacenados en la base de datos PostgreSQL.
    Soporta paginación opcional mediante limit y offset.
    """
    estudiantes = students_repository.find_all(db, limit=limit, offset=offset)
    return estudiantes

@router.get("/{studentId}", response_model=Student, summary="Buscar estudiante por ID")
def find_by_id(studentId: str, db: Session = Depends(get_db)):
    """
    Obtiene los detalles de un estudiante específico según su UUID/ID.
    """
    estudiante = students_repository.find_by_id(db, studentId)
    if not estudiante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El estudiante con ID '{studentId}' no fue encontrado."
        )
    return estudiante

@router.post("", status_code=status.HTTP_201_CREATED, response_model=Student, summary="Crear un nuevo estudiante")
def create(body: CreateStudentDto, db: Session = Depends(get_db)):
    """
    Crea un nuevo estudiante validando que el correo electrónico no esté duplicado.
    """
    # Validación extra de negocio para evitar duplicados
    if hasattr(body, 'email') and body.email:
        existente = students_repository.find_by_email(db, body.email)
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un estudiante registrado con este correo electrónico."
            )
            
    return students_repository.create(db, body)

@router.patch("/{studentId}", response_model=Student, summary="Actualizar datos de un estudiante")
def update(studentId: str, body: UpdateStudentDto, db: Session = Depends(get_db)):
    """
    Actualiza parcialmente la información de un estudiante existente.
    """
    estudiante = students_repository.update(db, studentId, body)
    if not estudiante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se pudo actualizar: el estudiante con ID '{studentId}' no existe."
        )
    return estudiante

@router.delete("/{studentId}", response_model=Student, summary="Eliminar un estudiante")
def delete(studentId: str, db: Session = Depends(get_db)):
    """
    Elimina un estudiante de la base de datos y remueve sus dependencias asociadas.
    """
    deleted = students_repository.delete(db, studentId)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se pudo eliminar: el estudiante con ID '{studentId}' no existe."
        )
    pets_service.delete_all_for_student(studentId)
    return deleted
