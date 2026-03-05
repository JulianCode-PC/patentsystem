from pydantic import BaseModel
from typing import Optional
from datetime import date

class CaseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    deadline: Optional[date] = None

class CaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[date] = None

class CaseOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    deadline: Optional[date]

    class Config:
        orm_mode = True