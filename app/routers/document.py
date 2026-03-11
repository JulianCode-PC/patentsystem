from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import shutil
import os
from datetime import datetime

from app.database import get_db
from app.models.document import Document
from app.models.case import Case
from app.schemas.document import DocumentOut
from app.services.pdf_service import PDFService

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 🔥 修改：不再需要 case_id，直接上傳後自動對應
@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    """
    上傳文件，自動從 PDF 讀取申請案號
    - 有申請案號 → 對應到現有案件
    - 無申請案號 → 建立新案件
    """
    # 儲存檔案
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # 處理 PDF（自動找或建立 Case）
    try:
        doc, case = PDFService.save_pdf_to_db(db, file_location, file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"處理失敗: {str(e)}")

    # 重新導向到該案件的上傳頁
    return RedirectResponse(url=f"/cases/{case.id}/upload", status_code=303)

# 其餘 API 不變
@router.get("/case/{case_id}")
def get_documents(case_id: int, db: Session = Depends(get_db)):
    docs = db.query(Document).filter(Document.case_id == case_id).all()
    return docs

@router.get("/{document_id}/extracted-info")
def get_extracted_info(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    days_remaining = None
    if doc.deadline:
        days_remaining = (doc.deadline - datetime.now()).days
    
    return {
        "filename": doc.filename,
        "doc_type": doc.doc_type,
        "extracted_data": doc.extracted_data,
        "deadline": doc.deadline,
        "days_remaining": days_remaining,
        "is_expiring_soon": days_remaining and days_remaining <= 7
    }

@router.post("/{document_id}/reprocess")
def reprocess_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    from app.services.classifier import classifier
    result = classifier.process_document(doc.text_content, doc.uploaded_at)
    
    doc.doc_type = result["doc_type"]
    doc.extracted_data = result["extracted_data"]
    doc.deadline = result["deadline"]
    doc.deadline_days = result["deadline_days"]
    
    db.commit()
    
    return {"message": "重新處理完成", "result": result}

# 新增：即將到期 API
@router.get("/expiring-soon")
def get_expiring_documents(days: int = 7, db: Session = Depends(get_db)):
    from datetime import datetime, timedelta
    now = datetime.now()
    cutoff = now + timedelta(days=days)
    
    docs = db.query(Document).filter(
        Document.deadline.isnot(None),
        Document.deadline <= cutoff,
        Document.deadline >= now
    ).order_by(Document.deadline).all()
    
    return docs