'''
document.py 定義了 Document 資料表（documents） 
的 ORM 類別，用來儲存 每個專利案件相關的文件。


功能包括：

紀錄文件基本資訊（檔名、檔案路徑、上傳時間）

關聯到對應的 Case

支援 ORM CRUD 操作（新增、查詢、修改、刪除）
'''

# document.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
#建立 ORM 的 物件關聯
from sqlalchemy.orm import relationship
#Document 需要繼承 Base 才能被 ORM 識別為資料表
from app.database import Base
from datetime import datetime, timezone

#定義 Document 類別
class Document(Base):
    #對應資料庫表名 documents
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    #nullable=False → 每個文件 一定要關聯到一個案件
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    case = relationship("Case", back_populates="documents")