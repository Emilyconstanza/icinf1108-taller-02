from fastapi import APIRouter, Depends, HTTPException, status
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

@router.get("", response_model=StudentList)
def find_all(db: Session = Depends(get_db)):
    return students_repository.find_all(db)

@router.get("/{studentId}", response_model=Student)
def find_by_id(studentId: str, db: Session = Depends(get_db)):
    estudiante = students_repository.find_by_id(db, studentId)
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return estudiante

@router.post("", status_code=status.HTTP_201_CREATED, response_model=Student)
def create(body: CreateStudentDto, db: Session = Depends(get_db)):
    return students_repository.create(db, body)

@router.patch("/{studentId}", response_model=Student)
def update(studentId: str, body: UpdateStudentDto, db: Session = Depends(get_db)):
    estudiante = students_repository.update(db, studentId, body)
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return estudiante

@router.delete("/{studentId}", response_model=Student)
def delete(studentId: str, db: Session = Depends(get_db)):
    deleted = students_repository.delete(db, studentId)
    if not deleted:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    pets_service.delete_all_for_student(studentId)
    return deleted
