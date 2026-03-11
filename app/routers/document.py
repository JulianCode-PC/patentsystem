from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List
import shutil
import os
from datetime import datetime, timedelta

from app.database import get_db
from app.models.document import Document
from app.models.case import Case
from app.schemas.document import DocumentOut
from app.services.pdf_service import PDFService
from app.services.classifier import classifier

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 上傳文件並自動處理
@router.post("/upload/{case_id}", response_model=DocumentOut)
async def upload_document(
    case_id: int, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    # 檢查案件
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # 儲存檔案
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # 使用 PDFService 處理（包含分類和期限）
    try:
        doc = PDFService.save_pdf_to_db(db, case_id, file_location, file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"處理失敗: {str(e)}")

    return doc

# 查詢案件的相關文件（含分類資訊）
@router.get("/case/{case_id}", response_model=List[DocumentOut])
def get_documents(case_id: int, db: Session = Depends(get_db)):
    docs = db.query(Document).filter(Document.case_id == case_id).all()
    return docs

# 取得文件抽取的關鍵資訊
@router.get("/{document_id}/extracted-info")
def get_extracted_info(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # 計算剩餘天數
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

# 手動重新處理文件
@router.post("/{document_id}/reprocess")
def reprocess_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # 重新處理
    result = classifier.process_document(doc.text_content, doc.uploaded_at)
    
    # 更新資料庫
    doc.doc_type = result["doc_type"]
    doc.extracted_data = result["extracted_data"]
    doc.deadline = result["deadline"]
    doc.deadline_days = result["deadline_days"]
    
    db.commit()
    
    return {"message": "重新處理完成", "result": result}

# 🚀 **新增：即將到期文件 API**
@router.get("/expiring-soon", response_model=List[DocumentOut])
def get_expiring_documents(
    days: int = Query(7, description="幾天內到期（預設7天）"),
    db: Session = Depends(get_db)
):
    """
    列出即將到期的文件
    - days: 幾天內到期 (預設7天)
    """
    now = datetime.now()
    cutoff = now + timedelta(days=days)
    
    docs = db.query(Document).filter(
        Document.deadline.isnot(None),  # 有截止日的才列
        Document.deadline <= cutoff,    # 在截止日之前
        Document.deadline >= now        # 還沒過期
    ).order_by(Document.deadline.asc()).all()  # 快到期的排在前面
    
    return docs