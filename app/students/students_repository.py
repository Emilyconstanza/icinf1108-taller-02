from typing import Optional
from sqlalchemy.orm import Session
from app.models import Student  # Ajusta según el nombre de tu modelo ORM
from app.students.students_schemas import CreateStudentDto, UpdateStudentDto

class StudentsRepository:
    def find_all(self, db: Session, limit: int = 100, offset: int = 0):
        """Obtiene la lista de estudiantes con paginación básica."""
        return db.query(Student).order_by(Student.id).offset(offset).limit(limit).all()

    def find_by_id(self, db: Session, student_id: str) -> Optional[Student]:
        """Busca un estudiante por su ID único."""
        return db.query(Student).filter(Student.id == student_id).first()

    def find_by_email(self, db: Session, email: str) -> Optional[Student]:
        """Verifica si ya existe un estudiante registrado con el mismo correo."""
        return db.query(Student).filter(Student.email == email).first()

    def create(self, db: Session, dto: CreateStudentDto) -> Student:
        """Crea y persiste un nuevo registro de estudiante en PostgreSQL."""
        nuevo_estudiante = Student(**dto.model_dump())
        db.add(nuevo_estudiante)
        db.commit()
        db.refresh(nuevo_estudiante)
        return nuevo_estudiante

    def update(self, db: Session, student_id: str, dto: UpdateStudentDto) -> Optional[Student]:
        """Actualiza parcialmente los datos de un estudiante existente."""
        estudiante = self.find_by_id(db, student_id)
        if not estudiante:
            return None
        
        # Filtra únicamente los campos enviados en el payload
        datos_actualizar = dto.model_dump(exclude_unset=True)
        for clave, valor in datos_actualizar.items():
            setattr(estudiante, clave, valor)

        db.commit()
        db.refresh(estudiante)
        return estudiante

    def delete(self, db: Session, student_id: str) -> Optional[Student]:
        """Elimina la entidad de la base de datos."""
        estudiante = self.find_by_id(db, student_id)
        if not estudiante:
            return None
        db.delete(estudiante)
        db.commit()
        return estudiante

students_repository = StudentsRepository()
