from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.pets.pets_schemas import CreatePetDto


class CreateStudentDto(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    pets: list[CreatePetDto] = Field(default_factory=list)


class UpdateStudentDto(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class Student(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: Optional[str] = None


class StudentList(BaseModel):
    total: int
    items: list[Student]
