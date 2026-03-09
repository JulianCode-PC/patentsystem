from pydantic import BaseModel
from datetime import datetime

class DocumentBase(BaseModel):
    filename: str
    filepath: str
    case_id: int

class DocumentCreate(DocumentBase):
    pass

class DocumentOut(DocumentBase):
    id: int
    upload_time: datetime

    class Config:
        orm_mode = True