from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class DocumentBase(BaseModel):
    filename: str
    file_path: str  #統一用 file_path
    case_id: int

class DocumentCreate(DocumentBase):
    pass

class DocumentOut(DocumentBase):
    id: int
    uploaded_at: datetime  # 你原本寫 upload_time，統一用 uploaded_at
    text_content: Optional[str] = None
    
    # Day5 新增
    doc_type: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    deadline: Optional[datetime] = None
    deadline_days: Optional[int] = None

    class Config:
        orm_mode = True
        from_attributes = True  # Pydantic v2