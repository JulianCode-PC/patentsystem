import os
import pdfplumber
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Tuple

from app.models.document import Document
from app.models.case import Case
from app.services.classifier import classifier

class PDFService:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """從 PDF 抓文字"""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"PDF 文字抽取失敗: {e}")
        return text

    @staticmethod
    def save_pdf_to_db(db: Session, file_path: str, filename: str) -> Tuple[Document, Case]:
        """
        抓文字、分類、找案件、存資料庫
        回傳: (Document, Case)
        """
        # 1. 抓文字
        text = PDFService.extract_text_from_pdf(file_path)
        
        # 2. 用規則引擎處理
        result = classifier.process_document(text)
        
        # 3. 從結果取得申請案號和專利名稱
        fields = result["extracted_data"]["fields"]
        app_number = fields.get("application_number")
        title = fields.get("invention_title", "新專利案件")
        applicant = fields.get("applicant", "")
        
        # 4. 用申請案號找或建立 Case
        case = None
        if app_number:
            case = db.query(Case).filter(Case.case_no == app_number).first()
        
        if not case:
            # 沒有找到 → 建立新案件
            case = Case(
                case_no=app_number or f"TEMP{datetime.now().strftime('%Y%m%d%H%M%S')}",
                title=title,
                applicant=applicant,
                status="進行中"
            )
            db.add(case)
            db.commit()
            db.refresh(case)
        
        # 5. 建立 Document（關聯到找到/建立的 case）
        document = Document(
            case_id=case.id,  # 這裡用 case.id！
            filename=filename,
            file_path=file_path,
            uploaded_at=datetime.now(timezone.utc),
            text_content=text,
            doc_type=result["doc_type"],
            extracted_data=result["extracted_data"],
            deadline=result["deadline"],
            deadline_days=result["deadline_days"]
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        return document, case