from sqlalchemy.orm import Session
from app.models import Student  # Reemplaza o ajusta el nombre del modelo según tu app.models
from app.students.students_schemas import CreateStudentDto, UpdateStudentDto

class StudentsRepository:
    def find_all(self, db: Session):
        return db.query(Student).all()

    def find_by_id(self, db: Session, student_id: str):
        return db.query(Student).filter(Student.id == student_id).first()

    def create(self, db: Session, dto: CreateStudentDto):
        nuevo_estudiante = Student(**dto.model_dump())
        db.add(nuevo_estudiante)
        db.commit()
        db.refresh(nuevo_estudiante)
        return nuevo_estudiante

    def update(self, db: Session, student_id: str, dto: UpdateStudentDto):
        estudiante = self.find_by_id(db, student_id)
        if not estudiante:
            return None
        for key, value in dto.model_dump(exclude_unset=True).items():
            setattr(estudiante, key, value)
        db.commit()
        db.refresh(estudiante)
        return estudiante

    def delete(self, db: Session, student_id: str):
        estudiante = self.find_by_id(db, student_id)
        if not estudiante:
            return None
        db.delete(estudiante)
        db.commit()
        return estudiante

students_repository = StudentsRepository()
