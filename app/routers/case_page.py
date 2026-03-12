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

# 儀表板
@router.get("/cases", response_class=HTMLResponse)
def case_list(request: Request, db: Session = Depends(get_db)):
    cases = db.query(Case).all()
    now = datetime.now()
    today = now.date()
    
    cutoff = now + timedelta(days=7)
    
    expiring_count = db.query(Document).filter(
        Document.deadline.isnot(None),
        Document.deadline <= cutoff,
        Document.deadline >= now
    ).count()
    
    for case in cases:
        min_deadline = None
        for doc in case.documents:
            if doc.deadline:
                doc_date = doc.deadline.date() if hasattr(doc.deadline, 'date') else doc.deadline
                if not min_deadline or doc_date < min_deadline:
                    min_deadline = doc_date
        case.min_deadline = min_deadline
    
    return templates.TemplateResponse("case_list.html", {
        "request": request,
        "cases": cases,
        "expiring_count": expiring_count,
        "now": now,
        "today": today
    })

# 案件詳情
@router.get("/cases/{case_id}", response_class=HTMLResponse)
def case_detail(request: Request, case_id: int, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="案件不存在")
    
    return templates.TemplateResponse("case_detail.html", {
        "request": request,
        "case": case,
        "now": datetime.now()
    })

# 顯示編輯表單
@router.get("/cases/{case_id}/edit", response_class=HTMLResponse)
def case_edit_page(request: Request, case_id: int, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="案件不存在")
    
    return templates.TemplateResponse("case_edit.html", {
        "request": request,
        "case": case
    })

# 處理編輯表單提交
@router.post("/cases/{case_id}/edit", response_class=HTMLResponse)
def case_edit_submit(
    request: Request, 
    case_id: int, 
    case_no: str = Form(...),
    title: str = Form(...),
    applicant: str = Form(None),
    filing_date: str = Form(None),
    status: str = Form(...),
    deadline: str = Form(None),
    db: Session = Depends(get_db)
):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="案件不存在")
    
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
    
    db.commit()
    
    return RedirectResponse(url=f"/cases/{case.id}", status_code=303)

# 刪除案件
@router.post("/cases/{case_id}/delete", response_class=HTMLResponse)
def case_delete(case_id: int, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="案件不存在")
    
    db.delete(case)
    db.commit()
    
    return RedirectResponse(url="/cases", status_code=303)

# 上傳頁
@router.get("/cases/{case_id}/upload", response_class=HTMLResponse)
def upload_page(request: Request, case_id: int, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="案件不存在")
    
    return templates.TemplateResponse("case_upload.html", {
        "request": request,
        "case": case,
        "now": datetime.now()
    })

# 統一上傳頁
@router.get("/upload", response_class=HTMLResponse)
def unified_upload_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("unified_upload.html", {
        "request": request,
        "now": datetime.now()
    })


# 🔥 文件編輯頁面
@router.get("/documents/{document_id}/edit", response_class=HTMLResponse)
def document_edit_page(request: Request, document_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return templates.TemplateResponse("document_edit.html", {
        "request": request,
        "doc": doc,
        "now": datetime.now()
    })

# 🔥 處理文件編輯表單提交
@router.post("/documents/{document_id}/edit", response_class=HTMLResponse)
def document_edit_submit(
    request: Request,
    document_id: int,
    filename: str = Form(...),  # 🔥 新增
    doc_type: str = Form(None),
    deadline: str = Form(None),
    application_number: str = Form(None),  # 隱藏欄位
    invention_title: str = Form(None),     # 隱藏欄位
    applicant: str = Form(None),           # 隱藏欄位
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 🔥 更新檔案名稱
    doc.filename = filename
    
    # 更新文件類型
    if doc_type:
        doc.doc_type = doc_type
    
    # 更新截止日
    if deadline:
        doc.deadline = datetime.strptime(deadline, "%Y-%m-%d")
    else:
        doc.deadline = None
    
    # 保留原本的 extracted_data（不讓使用者修改，但用隱藏欄位保留）
    if not doc.extracted_data:
        doc.extracted_data = {"fields": {}, "dates": {}}
    
    if "fields" not in doc.extracted_data:
        doc.extracted_data["fields"] = {}
    
    # 只更新隱藏欄位傳過來的值（等於保留原值）
    if application_number:
        doc.extracted_data["fields"]["application_number"] = application_number
    
    if invention_title:
        doc.extracted_data["fields"]["invention_title"] = invention_title
    
    if applicant:
        doc.extracted_data["fields"]["applicant"] = applicant
    
    db.commit()
    
    return RedirectResponse(url=f"/cases/{doc.case_id}", status_code=303)