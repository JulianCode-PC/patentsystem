
'''
database.py 作用：

1.建立「資料庫連線引擎」
2.建立「ORM 基底類別」
3.提供「每次請求用的 Session」

'''

#create_engine 建立資料庫連線
from sqlalchemy import create_engine

#sessionmaker 建立 Session 工廠；declarative_base 是ORM基底，資料表的祖先
from sqlalchemy.orm import sessionmaker, declarative_base

# MySQL 連線字串格式:
# "mysql+pymysql://<username>:<password>@<host>:<port>/<database>?charset=utf8mb4"
DATABASE_URL = "mysql+pymysql://root:iaef2202@localhost:3306/patent_system_db?charset=utf8mb4"

#告訴SQLAlchemy，要連線的MySQL資料庫
#ORM就知道要存的資料要放哪
engine = create_engine(DATABASE_URL, echo=True)  # echo=True 會印出 SQL 對於debug有用

#sessionmaker 是SQLAlchemy提供的一個類別工廠(factory function)
#會回傳一個「Session 類別」，之後呼叫他db = SessionLocal()去建立Session物件。
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#declarative_base 是SQLAlchemy 提供的函式，產生一個 ORM 的「基底類別」
#SQLAlchemy 的 ORM 規則是：任何資料表 class 都必須繼承同一個 Base。
#Base能記錄所有資料表、建立資料表
Base = declarative_base()

# Dependency: 在 route 使用時取得 db session
def get_db(): 
    #建一個 Session 物件來操作資料庫；SessionLocal 是「類別」；db 是「物件」；engine 是「連線管理器」
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

