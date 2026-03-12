from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    text_content = Column(Text, nullable=True)
    
    # 新增這三行！
    doc_type = Column(String(100), nullable=True)  # 文件類型
    extracted_data = Column(JSON, nullable=True)   # 抽出的欄位
    deadline = Column(DateTime, nullable=True)     # 截止日
    deadline_days = Column(Integer, nullable=True) # 期限天數

    case = relationship("Case", back_populates="documents")