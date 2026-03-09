'''
ORM 資料表定義檔：定義資料結構：
告訴ORM說：資料表長什麼樣子，以及表之間怎麼連。
定義了 MySQL 裡的 cases 這張資料表長什麼樣子

1.定義 cases 資料表
2.定義欄位型別
3.定義和 documents 的關聯

'''

# case.py

#欄位型別，Column > 宣告資料表欄位，可以指定型別、設定限制
#Integer > 整數；String > 字串；DateTime>日期時間
from sqlalchemy import Column, Integer, String, DateTime,Date

#用來建立資料表之間的關聯（外鍵關係）。
from sqlalchemy.orm import relationship

#必須繼承 Base，ORM 才知道這是一張資料表。
from app.database import Base

#產生預設時間
from datetime import datetime, timezone

#Case 是一個 ORM 映射類別，會對應到一張資料表，因為繼承Base
class Case(Base):
    #資料庫裡這張表叫：cases
    __tablename__ = "cases"

    #整數型別、主鍵、有索引加快索引
    id = Column(Integer, primary_key=True, index=True)
    #字串型別、最大255字，不可為NULL
    title = Column(String(255), nullable=False)
    #字串型別、最大1000字，可以是NULL
    description = Column(String(1000), nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    #關聯定義，建立 ORM 關聯。，一個 Case 可以有多個 Document
    #Document 裡會有 case_id 外鍵
    documents = relationship("Document", back_populates="case")
    deadline = Column(Date, nullable=True)


'''
這個 class 最終會變成：

CREATE TABLE cases (
    id INT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description VARCHAR(1000),
    created_at DATETIME
);
'''