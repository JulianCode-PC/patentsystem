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