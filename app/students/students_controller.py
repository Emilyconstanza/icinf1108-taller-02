from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Pet, Student as StudentModel
from app.students.students_repository import students_repository
from app.students.students_schemas import (
    CreateStudentDto,
    Student,
    StudentList,
    UpdateStudentDto,
)

router = APIRouter(prefix="/api/students", tags=["Students"])


@router.get("", response_model=StudentList, summary="Obtener todos los estudiantes")
def find_all(
    limit: int = Query(default=100, ge=1, le=500, description="Límite de registros"),
    offset: int = Query(default=0, ge=0, description="Desplazamiento para paginación"),
    db: Session = Depends(get_db),
):
    students = students_repository.find_all(db, limit=limit, offset=offset)
    return StudentList(total=len(students), items=students)


@router.get("/{studentId}", response_model=Student, summary="Buscar estudiante por ID")
def find_by_id(studentId: str, db: Session = Depends(get_db)):
    student = students_repository.find_by_id(db, studentId)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El estudiante con ID '{studentId}' no fue encontrado.",
        )
    return student


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=Student,
    summary="Crear estudiante y mascotas en una transacción",
)
def create(body: CreateStudentDto, db: Session = Depends(get_db)):
    """Persist the student and all nested pets atomically."""
    if body.email and students_repository.find_by_email(db, str(body.email)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo electrónico ya está en uso",
        )

    pet_names = [pet.name for pet in body.pets]
    if len(pet_names) != len(set(pet_names)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya tienes una mascota con ese nombre",
        )

    student = StudentModel(name=body.name, email=str(body.email) if body.email else None)
    try:
        db.add(student)
        db.flush()  # Obtiene el ID antes de asociar las mascotas.
        db.add_all(
            [
                Pet(
                    student_id=student.id,
                    name=pet.name,
                    species=pet.species,
                    age=pet.age,
                )
                for pet in body.pets
            ]
        )
        db.commit()

        return student
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo guardar el estudiante y sus mascotas por un conflicto de datos.",
        ) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo completar la transacción de creación.",
        ) from exc


@router.patch("/{studentId}", response_model=Student, summary="Actualizar datos de un estudiante")
def update(studentId: str, body: UpdateStudentDto, db: Session = Depends(get_db)):
    student = students_repository.update(db, studentId, body)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se pudo actualizar: el estudiante con ID '{studentId}' no existe.",
        )
    return student


@router.delete("/{studentId}", response_model=Student, summary="Eliminar un estudiante")
def delete(studentId: str, db: Session = Depends(get_db)):
    student = students_repository.find_by_id(db, studentId)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se pudo eliminar: el estudiante con ID '{studentId}' no existe.",
        )
    try:
        db.delete(student)
        db.commit()
        return student
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo completar la transacción de eliminación.",
        ) from exc
