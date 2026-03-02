from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# MySQL 連線字串格式:
# "mysql+pymysql://<username>:<password>@<host>:<port>/<database>?charset=utf8mb4"
DATABASE_URL = "mysql+pymysql://root:iaef2202@localhost:3306/patent_system_db?charset=utf8mb4"

engine = create_engine(DATABASE_URL, echo=True)  # echo=True 會印出 SQL
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency: 在 route 使用時取得 db session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()