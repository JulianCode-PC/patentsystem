# app/routers/case_page.py
# 功能：處理所有「顯示網頁」的請求，回傳 HTML 給瀏覽器
# 資料流方向：瀏覽器 → FastAPI → 資料庫 → 模板 → 瀏覽器

from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app.models.case import Case
from app.models.document import Document

router = APIRouter(tags=["Pages"])
templates = Jinja2Templates(directory="templates")


# ============================================================================
# 儀表板（案件列表頁面）
# ============================================================================
# 輸入：瀏覽器 GET 請求（網址 /cases）
# 處理：
#   1. 從資料庫讀取所有案件（db.query(Case).all()）
#   2. 從資料庫計算即將到期文件數量
#   3. 計算每個案件的最早文件截止日
# 輸出：HTML 網頁（case_list.html）→ 回傳給瀏覽器
# ============================================================================
@router.get("/cases", response_class=HTMLResponse)
def case_list(request: Request, db: Session = Depends(get_db)):
    # ↓ 輸入：從資料庫讀取
    cases = db.query(Case).all()
    
    now = datetime.now()
    today = now.date()
    cutoff = now + timedelta(days=7)
    
    # ↓ 輸入：從資料庫統計
    expiring_count = db.query(Document).filter(
        Document.deadline.isnot(None),
        Document.deadline <= cutoff,
        Document.deadline >= now
    ).count()
    
    # ↓ 處理：計算每個案件的最早文件截止日
    for case in cases:
        min_deadline = None
        for doc in case.documents:
            if doc.deadline:
                doc_date = doc.deadline.date() if hasattr(doc.deadline, 'date') else doc.deadline
                if not min_deadline or doc_date < min_deadline:
                    min_deadline = doc_date
        case.min_deadline = min_deadline
    
    # ↓ 輸出：渲染 HTML 並回傳給瀏覽器
    return templates.TemplateResponse("case_list.html", {
        "request": request,
        "cases": cases,
        "expiring_count": expiring_count,
        "now": now,
        "today": today
    })


# ============================================================================
# 案件詳情頁面
# ============================================================================
# 輸入：瀏覽器 GET 請求（網址 /cases/1，其中 1 是案件 ID）
# 處理：用 case_id 從資料庫查詢單一案件
# 輸出：HTML 網頁（case_detail.html）→ 回傳給瀏覽器
# ============================================================================
@router.get("/cases/{case_id}", response_class=HTMLResponse)
def case_detail(request: Request, case_id: int, db: Session = Depends(get_db)):
    # ↓ 輸入：用 case_id 從資料庫查詢
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="案件不存在")
    
    # ↓ 輸出：渲染 HTML 並回傳給瀏覽器
    return templates.TemplateResponse("case_detail.html", {
        "request": request,
        "case": case,
        "now": datetime.now()
    })


# ============================================================================
# 顯示編輯案件表單
# ============================================================================
# 輸入：瀏覽器 GET 請求（網址 /cases/1/edit，1 是案件 ID）
# 處理：用 case_id 從資料庫查詢案件（取得目前資料）
# 輸出：HTML 表單（case_edit.html，內含案件目前資料）→ 回傳給瀏覽器
# ============================================================================
@router.get("/cases/{case_id}/edit", response_class=HTMLResponse)
def case_edit_page(request: Request, case_id: int, db: Session = Depends(get_db)):
    # ↓ 輸入：從資料庫讀取要編輯的案件
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="案件不存在")
    
    # ↓ 輸出：顯示編輯表單（填入案件目前的資料）
    return templates.TemplateResponse("case_edit.html", {
        "request": request,
        "case": case
    })


# ============================================================================
# 處理編輯案件表單提交
# ============================================================================
# 輸入：瀏覽器 POST 請求（表單提交），包含：
#   - 網址中的 case_id（要修改哪個案件）
#   - 表單欄位：case_no, title, applicant, filing_date, status, deadline
# 處理：用 case_id 找到案件，用表單資料更新案件
# 輸出：重新導向到案件詳情頁（瀏覽器跳轉到 /cases/{case_id}）
# ============================================================================
@router.post("/cases/{case_id}/edit", response_class=HTMLResponse)
def case_edit_submit(
    request: Request, 
    case_id: int, 
    # ↓ 輸入：從 POST 表單接收資料
    case_no: str = Form(...),
    title: str = Form(...),
    applicant: str = Form(None),
    filing_date: str = Form(None),
    status: str = Form(...),
    deadline: str = Form(None),
    db: Session = Depends(get_db)
):
    # ↓ 輸入：從資料庫讀取要修改的案件
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="案件不存在")
    
    # ↓ 處理：用表單資料更新案件物件
    case.case_no = case_no
    case.title = title
    case.applicant = applicant if applicant else None
    case.status = status
    
    if filing_date:
        case.filing_date = datetime.strptime(filing_date, "%Y-%m-%d")
    else:
        case.filing_date = None
        
    if deadline:
        case.deadline = datetime.strptime(deadline, "%Y-%m-%d").date()
    else:
        case.deadline = None
    
    # ↓ 輸出：將更新寫入資料庫
    db.commit()
    
    # ↓ 輸出：重新導向到案件詳情頁
    return RedirectResponse(url=f"/cases/{case.id}", status_code=303)


# ============================================================================
# 刪除案件
# ============================================================================
# 輸入：瀏覽器 POST 請求（網址 /cases/1/delete，1 是案件 ID）
# 處理：用 case_id 找到案件，從資料庫刪除
# 輸出：重新導向到儀表板（瀏覽器跳轉到 /cases）
# ============================================================================
@router.post("/cases/{case_id}/delete", response_class=HTMLResponse)
def case_delete(case_id: int, db: Session = Depends(get_db)):
    # ↓ 輸入：從資料庫讀取要刪除的案件
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="案件不存在")
    
    # ↓ 處理：從資料庫刪除（會連帶刪除文件）
    db.delete(case)
    db.commit()
    
    # ↓ 輸出：重新導向到儀表板
    return RedirectResponse(url="/cases", status_code=303)


# ============================================================================
# 顯示上傳文件頁面（特定案件）
# ============================================================================
# 輸入：瀏覽器 GET 請求（網址 /cases/1/upload，1 是案件 ID）
# 處理：用 case_id 查詢案件（取得案件資訊）
# 輸出：HTML 上傳頁面（case_upload.html）→ 回傳給瀏覽器
# ============================================================================
@router.get("/cases/{case_id}/upload", response_class=HTMLResponse)
def upload_page(request: Request, case_id: int, db: Session = Depends(get_db)):
    # ↓ 輸入：從資料庫讀取案件
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="案件不存在")
    
    # ↓ 輸出：顯示上傳頁面
    return templates.TemplateResponse("case_upload.html", {
        "request": request,
        "case": case,
        "now": datetime.now()
    })


# ============================================================================
# 統一上傳頁面
# ============================================================================
# 輸入：瀏覽器 GET 請求（網址 /upload）
# 處理：不需要查詢資料庫
# 輸出：HTML 統一上傳頁面（unified_upload.html）→ 回傳給瀏覽器
# ============================================================================
@router.get("/upload", response_class=HTMLResponse)
def unified_upload_page(request: Request, db: Session = Depends(get_db)):
    # ↓ 輸出：顯示統一上傳頁面（不依賴特定案件）
    return templates.TemplateResponse("unified_upload.html", {
        "request": request,
        "now": datetime.now()
    })


# ============================================================================
# 顯示編輯文件表單
# ============================================================================
# 輸入：瀏覽器 GET 請求（網址 /documents/1/edit，1 是文件 ID）
# 處理：用 document_id 從資料庫查詢文件
# 輸出：HTML 編輯表單（document_edit.html，內含文件目前資料）→ 回傳給瀏覽器
# ============================================================================
@router.get("/documents/{document_id}/edit", response_class=HTMLResponse)
def document_edit_page(request: Request, document_id: int, db: Session = Depends(get_db)):
    # ↓ 輸入：從資料庫讀取要編輯的文件
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # ↓ 輸出：顯示編輯表單（填入文件目前的資料）
    return templates.TemplateResponse("document_edit.html", {
        "request": request,
        "doc": doc,
        "now": datetime.now()
    })


# ============================================================================
# 處理編輯文件表單提交
# ============================================================================
# 輸入：瀏覽器 POST 請求（表單提交），包含：
#   - 網址中的 document_id（要修改哪個文件）
#   - 表單欄位：filename, doc_type, deadline, 以及隱藏欄位
# 處理：用 document_id 找到文件，用表單資料更新文件
# 輸出：重新導向到該文件所屬的案件詳情頁
# ============================================================================
@router.post("/documents/{document_id}/edit", response_class=HTMLResponse)
def document_edit_submit(
    request: Request,
    document_id: int,
    # ↓ 輸入：從 POST 表單接收資料
    filename: str = Form(...),
    doc_type: str = Form(None),
    deadline: str = Form(None),
    application_number: str = Form(None),
    invention_title: str = Form(None),
    applicant: str = Form(None),
    db: Session = Depends(get_db)
):
    # ↓ 輸入：從資料庫讀取要修改的文件
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # ↓ 處理：用表單資料更新文件物件
    doc.filename = filename
    
    if doc_type:
        doc.doc_type = doc_type
    
    if deadline:
        doc.deadline = datetime.strptime(deadline, "%Y-%m-%d")
    else:
        doc.deadline = None
    
    # 保留原本的 OCR 資料（從隱藏欄位寫回）
    if not doc.extracted_data:
        doc.extracted_data = {"fields": {}, "dates": {}}
    
    if "fields" not in doc.extracted_data:
        doc.extracted_data["fields"] = {}
    
    if application_number:
        doc.extracted_data["fields"]["application_number"] = application_number
    if invention_title:
        doc.extracted_data["fields"]["invention_title"] = invention_title
    if applicant:
        doc.extracted_data["fields"]["applicant"] = applicant
    
    # ↓ 輸出：將更新寫入資料庫
    db.commit()
    
    # ↓ 輸出：重新導向回該文件所屬的案件詳情頁
    return RedirectResponse(url=f"/cases/{doc.case_id}", status_code=303)