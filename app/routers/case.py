#用來建立一個 router，也就是一組 API 路徑的集合
#在 main.py 裡，我們會把這個 router 加入到 FastAPI 應用程式裡，讓它成為 API 的一部分。
#Depends → FastAPI 的 依賴注入db: Session = Depends(get_db)
#這行意思是「給每個 API 一個資料庫 session 使用」，get_db() 是在 database.py 定義的函數，會提供一個資料庫連線，使用完後自動關閉。
#HTTPException → API 回傳錯誤，例如找不到某個案件就要回 404：
from fastapi import APIRouter, Depends, HTTPException 

#Session 是 SQLAlchemy 的 資料庫操作物件，讓我們可以對資料庫進行 CRUD 操作。
from sqlalchemy.orm import Session

#FastAPI 用 Pydantic model 定義 response
from typing import List

#database.py 裡有這個 function，提供 每個 API 一個資料庫 session
from app.database import get_db

#對應資料庫的 cases 表，Case 是在 models/case.py 定義的 ORM 類別
from app.models.case import Case

#用來 驗證輸入資料 & 定義 API 回傳格式
from app.schemas.case import CaseCreate, CaseUpdate, CaseOut

router = APIRouter(prefix="/cases", tags=["cases"])

# 新增案件
@router.post("/", response_model=CaseOut)
def create_case(case: CaseCreate, db: Session = Depends(get_db)):
    db_case = Case(**case.dict())
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case

# 查詢全部案件
@router.get("/", response_model=List[CaseOut])
def read_cases(db: Session = Depends(get_db)):
    return db.query(Case).all()

# 查詢單一案件
@router.get("/{case_id}", response_model=CaseOut)
def read_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

# 修改案件
@router.put("/{case_id}", response_model=CaseOut)
def update_case(case_id: int, case_update: CaseUpdate, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    for key, value in case_update.dict(exclude_unset=True).items():
        setattr(case, key, value)
    db.commit()
    db.refresh(case)
    return case

# 刪除案件
@router.delete("/{case_id}")
def delete_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    db.delete(case)
    db.commit()
    return {"detail": "Case deleted"}