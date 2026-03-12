from fastapi.responses import FileResponse
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import shutil
import os
from datetime import datetime

from app.database import get_db
from app.models.document import Document
from app.models.case import Case
from app.schemas.document import DocumentOut, DocumentUpdate
from app.services.pdf_service import PDFService

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 上傳文件（自動對應案件）
@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        doc, case = PDFService.save_pdf_to_db(db, file_location, file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"處理失敗: {str(e)}")

    return RedirectResponse(url=f"/cases/{case.id}/upload", status_code=303)

# 查詢案件的文件
@router.get("/case/{case_id}")
def get_documents(case_id: int, db: Session = Depends(get_db)):
    docs = db.query(Document).filter(Document.case_id == case_id).all()
    return docs

# 取得文件抽取資訊
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

# 🔥 更新文件
@router.put("/{document_id}", response_model=DocumentOut)
def update_document(
    document_id: int, 
    doc_update: DocumentUpdate, 
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    for key, value in doc_update.dict(exclude_unset=True).items():
        setattr(doc, key, value)
    
    db.commit()
    db.refresh(doc)
    return doc

# 🔥 重新分類（重新抓文字 + 分類）
@router.post("/{document_id}/reclassify")
def reclassify_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 重新從 PDF 抓文字
    new_text = PDFService.extract_text_from_pdf(doc.file_path)
    doc.text_content = new_text
    
    from app.services.classifier import classifier
    result = classifier.process_document(new_text, doc.uploaded_at)
    
    doc.doc_type = result["doc_type"]
    doc.extracted_data = result["extracted_data"]
    doc.deadline = result["deadline"]
    doc.deadline_days = result["deadline_days"]
    
    db.commit()
    
    return {"message": "重新分類完成", "result": result}

# 即將到期 API
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

# 文件下載
@router.get("/{document_id}/download")
def download_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="檔案實體不存在")
    
    return FileResponse(
        path=doc.file_path,
        filename=doc.filename,
        media_type='application/pdf'
    )

# 文件預覽
@router.get("/{document_id}/preview")
def preview_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="檔案實體不存在")
    
    return FileResponse(
        path=doc.file_path,
        filename=doc.filename,
        media_type='application/pdf',
        headers={"Content-Disposition": "inline"}
    )


