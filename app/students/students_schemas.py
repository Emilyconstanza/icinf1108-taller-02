from typing import Optional
from pydantic import BaseModel, EmailStr

class CreateStudentDto(BaseModel):
    name: str
    email: Optional[EmailStr] = None

class UpdateStudentDto(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class Student(BaseModel):
    id: str
    name: str
    email: Optional[str] = None

    class Config:
        from_attributes = True

class StudentList(BaseModel):
    __root__: list[Student]
