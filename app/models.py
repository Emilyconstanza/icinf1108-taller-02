from uuid import uuid4

from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Student(Base):
    """Student entity used by the API's relational persistence layer."""

    __tablename__ = "students"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True, unique=True, index=True)
    pets = relationship(
        "Pet", back_populates="student", cascade="all, delete-orphan"
    )


class Pet(Base):
    """Pet entity; its lifecycle is tied to its owning student."""

    __tablename__ = "pets"
    __table_args__ = (
        UniqueConstraint("student_id", "name", name="uq_pet_student_name"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    student_id = Column(
        String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(50), nullable=False)
    species = Column(String(50), nullable=False)
    age = Column(Integer, nullable=True)
    student = relationship("Student", back_populates="pets")
