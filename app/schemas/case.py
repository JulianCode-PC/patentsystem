from pydantic import BaseModel  # 匯入 Pydantic 的 BaseModel，所有 schema 都要繼承它
from typing import Optional      # 匯入 Optional，表示某欄位可以是 None（可選）
from datetime import date        # 匯入 date 型別，用來處理日期欄位

# -----------------------------
# 新增案件用的 schema
# -----------------------------
class CaseCreate(BaseModel):
    title: str                        # 必填欄位，案件標題，型別必須是字串
    description: Optional[str] = None # 可選欄位，案件描述，沒填會預設 None
    deadline: Optional[date] = None   # 可選欄位，截止日期，沒填會預設 None

# -----------------------------
# 修改案件用的 schema
# -----------------------------
class CaseUpdate(BaseModel):
    title: Optional[str] = None       # 可選欄位，修改時可以選擇性更新
    description: Optional[str] = None # 可選欄位，可選更新
    deadline: Optional[date] = None   # 可選欄位，可選更新

# -----------------------------
# 回傳給前端用的 schema
# -----------------------------
class CaseOut(BaseModel):
    id: int                           # 資料庫自動生成的 ID，回傳前端用
    title: str                        # 案件標題，必定存在
    description: Optional[str]        # 案件描述，可為 None
    deadline: Optional[date]          # 截止日期，可為 None

    class Config:
        orm_mode = True               # 告訴 Pydantic 可以直接從 ORM model（SQLAlchemy）讀取資料



'''
Pydantic 的 schema（像 CaseCreate、CaseUpdate、CaseOut）
就是「新的資料結構」，但它不是資料庫裡的 table，而是 API 用的資料規格。

1.CaseCreate 是資料結構，定義「新增案件時前端要送的資料長什麼樣」

例如 title 必填、description 可選、deadline 可選

這個結構只存在於 Python / FastAPI 的記憶體中，用來驗證和傳資料

2.和資料庫 Model 不一樣，Model（Case class）定義的是 DB table 的欄位

Schema（CaseCreate）定義的是 前端送入或後端回傳的資料格式，可以挑欄位、加驗證、改必填/可選

3.為什麼要新的資料結構？

新增案件時，前端不用傳 id → 用 CaseCreate
更新案件時，前端只想傳想改的欄位 → 用 CaseUpdate
回傳資料給前端時，可能不想回傳內部欄位 → 用 CaseOut

'''