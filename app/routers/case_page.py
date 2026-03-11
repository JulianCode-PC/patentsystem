from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app.models.case import Case
from app.models.document import Document

router = APIRouter(tags=["Pages"])
templates = Jinja2Templates(directory="templates")

@router.get("/cases", response_class=HTMLResponse)
def case_list(request: Request, db: Session = Depends(get_db)):
    cases = db.query(Case).all()
    now = datetime.now()
    today = now.date()  # 轉成 date
    
    cutoff = now + timedelta(days=7)
    
    expiring_count = db.query(Document).filter(
        Document.deadline.isnot(None),
        Document.deadline <= cutoff,
        Document.deadline >= now
    ).count()
    
    return templates.TemplateResponse("case_list.html", {
        "request": request,
        "cases": cases,
        "expiring_count": expiring_count,
        "now": now,
        "today": today  # 傳給模板
    })

@router.get("/cases/{case_id}/upload", response_class=HTMLResponse)
def upload_page(request: Request, case_id: int, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    return templates.TemplateResponse("case_upload.html", {
        "request": request,
        "case": case,
        "now": datetime.now()
    })