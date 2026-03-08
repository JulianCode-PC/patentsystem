# ------------------------------
# 匯入 FastAPI 相關工具
# ------------------------------
from fastapi import APIRouter, Depends, HTTPException  
# APIRouter → 建立一組 API 路徑集合（router）
# Depends → FastAPI 依賴注入，這裡用來自動提供資料庫 session
# HTTPException → 在 API 裡拋出錯誤，例如 404 找不到案件

# ------------------------------
# 匯入 SQLAlchemy 的 Session
# ------------------------------
from sqlalchemy.orm import Session  
# Session → 資料庫操作物件，用來 CRUD

# ------------------------------
# 匯入 List 型別，用在 response_model
# ------------------------------
from typing import List  

# ------------------------------
# 匯入提供資料庫連線的 function
# ------------------------------
from app.database import get_db  
# get_db() → 每個 API 會拿到一個 session，使用完自動關閉

# ------------------------------
# 匯入資料庫 model
# ------------------------------
from app.models.case import Case  
# Case → ORM 類別，對應資料庫 cases table

# ------------------------------
# 匯入 Pydantic schema
# ------------------------------
from app.schemas.case import CaseCreate, CaseUpdate, CaseOut  
# CaseCreate → 前端新增案件的資料規格
# CaseUpdate → 前端修改案件的資料規格
# CaseOut → 後端回傳前端的資料規格

# ------------------------------
# 建立一個 router，設定 prefix 與 tag
# ------------------------------
router = APIRouter(prefix="/cases", tags=["cases"])  
# prefix="/cases" → 所有路由都會自動加上 /cases 開頭
# tags → 在 Swagger UI 顯示分類名稱

# ------------------------------
# 新增案件 API
# ------------------------------
@router.post("/", response_model=CaseOut)  
# POST /cases/ → 新增案件的 API
#case: CaseCreate → 前端送過來的 JSON 會自動轉成 CaseCreate 的 Pydantic 物件，並驗證型別(case為變數名稱)
#db: Session = Depends(get_db)：依賴注入 (Dependency Injection)，每次呼叫這個 API 會拿到一個資料庫 session，可以操作資料庫
#get_db是在database.py裡定義的 function，會建立一個 session，提供給 API 使用，使用完後自動關閉連線

#Depends(get_db) 告訴 FastAPI：「這個 API 需要一個資料庫 session，請自動呼叫 get_db() 來生成」
#Session，可以做 CRUD
def create_case(case: CaseCreate, db: Session = Depends(get_db)):  
    # case → 前端送來的資料，型別是 CaseCreate，會自動驗證型別，是 Python 的資料結構，不是資料庫物件
    #case.model_dump() → 把 Pydantic 物件轉成 dict，準備傳給 ORM 物件
    db_case = Case(**case.model_dump())  
    # 把 schema 轉成 ORM 物件，準備存入資料庫
    db.add(db_case)  # 加入 session
    db.commit()     # 提交到資料庫
    db.refresh(db_case)  
    # 刷新 db_case，取得自動生成的 id 等欄位
    return db_case  # 回傳 CaseOut 給前端

# ------------------------------
# 查詢全部案件 API
# ------------------------------
@router.get("/", response_model=List[CaseOut])  
# GET /cases/ → 取得全部案件
def read_cases(db: Session = Depends(get_db)):
    return db.query(Case).all()  
    # 直接從資料庫查詢所有案件，回傳 List[CaseOut]

# ------------------------------
# 查詢單一案件 API
# ------------------------------
@router.get("/{case_id}", response_model=CaseOut)  
# GET /cases/{case_id} → 取得指定案件
def read_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()  
    # 查詢單筆資料
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")  
        # 找不到就回 404
    return case  # 回傳 CaseOut

# ------------------------------
# 修改案件 API
# ------------------------------
@router.put("/{case_id}", response_model=CaseOut)  
# PUT /cases/{case_id} → 更新指定案件
def update_case(case_id: int, case_update: CaseUpdate, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    for key, value in case_update.dict(exclude_unset=True).items():  
        # exclude_unset=True → 只更新有送值的欄位
        setattr(case, key, value)  # 把欄位更新到 ORM 物件
    db.commit()    # 提交更新
    db.refresh(case)  # 重新抓最新資料
    return case    # 回傳 CaseOut

# ------------------------------
# 刪除案件 API
# ------------------------------
@router.delete("/{case_id}")  
# DELETE /cases/{case_id} → 刪除指定案件
def delete_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    db.delete(case)  # 從 session 刪除
    db.commit()      # 提交刪除
    return {"detail": "Case deleted"}  
    # 回傳訊息給前端