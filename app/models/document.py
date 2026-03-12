from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    
    # 🔥 修改這行！加上 ondelete="CASCADE"
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    text_content = Column(Text, nullable=True)
    
    doc_type = Column(String(100), nullable=True)
    extracted_data = Column(JSON, nullable=True)
    deadline = Column(DateTime, nullable=True)
    deadline_days = Column(Integer, nullable=True)

    case = relationship("Case", back_populates="documents")