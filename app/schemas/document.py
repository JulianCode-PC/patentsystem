from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class DocumentBase(BaseModel):
    filename: str
    file_path: str
    case_id: int

class DocumentCreate(DocumentBase):
    pass

# 🔥 更新文件用的 schema
class DocumentUpdate(BaseModel):
    doc_type: Optional[str] = None
    deadline: Optional[datetime] = None
    extracted_data: Optional[Dict[str, Any]] = None

class DocumentOut(DocumentBase):
    id: int
    uploaded_at: datetime
    text_content: Optional[str] = None
    doc_type: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    deadline: Optional[datetime] = None
    deadline_days: Optional[int] = None

    class Config:
        from_attributes = True