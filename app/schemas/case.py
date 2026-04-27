"""
Pydantic Schema 定義檔
功能：定義 API 的資料格式（請求與回應的結構）
用途：驗證前端送來的資料、定義回傳給前端的資料格式
"""

from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

# ============================================================
# CaseCreate：新增案件時，前端「必須」送來的資料格式
# 使用場景：
#   1. 手動新增案件（POST /cases/）
#   2. 上傳 PDF 自動建立案件時，會用這個格式儲存
# 會影響的檔案：
#   - app/routers/case.py (create_case 函數)
#   - app/routers/case_page.py (create_case_manual 函數)
#   - app/services/pdf_service.py (save_pdf_to_db 函數，建立新案件時)
# ============================================================
class CaseCreate(BaseModel):
    case_no: str                      # 案號（必填），例如：TW113100001
    title: str                        # 專利名稱（必填）
    applicant: Optional[str] = None   # 申請人（可選），從 PDF 自動抓或手動輸入
    filing_date: Optional[date] = None # 申請日（可選），格式：YYYY-MM-DD
    status: Optional[str] = "進行中"   # 案件狀態（預設進行中），可選值：進行中、已結案
    deadline: Optional[date] = None   # 案件自訂截止日（可選），與文件截止日不同
    patent_type: Optional[str] = "發明專利"  # 專利類型（預設發明專利）


# ============================================================
# CaseUpdate：修改案件時，前端「可以選擇性」送來的資料格式
# 使用場景：
#   1. 編輯案件頁面提交表單（POST /cases/{case_id}/edit）
#   2. API 更新案件（PUT /cases/{case_id}）
# 特色：只更新有送值的欄位（exclude_unset=True）
# 會影響的檔案：
#   - app/routers/case.py (update_case 函數)
#   - app/routers/case_page.py (case_edit_submit 函數)
#   - templates/case_edit.html (編輯表單)
# ============================================================
class CaseUpdate(BaseModel):
    case_no: Optional[str] = None     # 案號（可選，修改時才送）
    title: Optional[str] = None       # 專利名稱（可選）
    applicant: Optional[str] = None   # 申請人（可選）
    filing_date: Optional[date] = None # 申請日（可選）
    status: Optional[str] = None      # 案件狀態（可選）
    deadline: Optional[date] = None   # 案件截止日（可選）
    patent_type: Optional[str] = None # 🔥 專利類型（可選）


# ============================================================
# CaseOut：回傳給前端的案件資料格式
# 使用場景：
#   1. 查詢案件列表時（GET /cases/）
#   2. 查詢單一案件時（GET /cases/{case_id}）
#   3. 儀表板顯示案件列表時
#   4. 案件詳情頁顯示案件基本資料時
# 會影響的檔案：
#   - app/routers/case.py (read_cases, read_case, update_case 等 API)
#   - app/routers/document.py (get_documents 等 API，可能關聯到 case)
#   - templates/case_list.html (顯示案件列表)
#   - templates/case_detail.html (顯示案件詳情)
#   - templates/case_edit.html (編輯表單載入資料)
# ============================================================
class CaseOut(BaseModel):
    id: int                           # 案件 ID（自動產生）
    case_no: str                      # 案號
    title: str                        # 專利名稱
    applicant: Optional[str] = None   # 申請人
    filing_date: Optional[date] = None # 申請日
    status: Optional[str] = None      # 案件狀態（進行中/已結案）
    deadline: Optional[date] = None   # 案件截止日
    patent_type: Optional[str] = None # 🔥 專利類型（發明/新型/設計）
    created_at: datetime              # 建立時間（自動產生）
    description: Optional[str] = None # 案件描述（預留欄位）

    class Config:
        # Pydantic v2 的寫法：允許從 ORM 物件直接轉換
        from_attributes = True




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