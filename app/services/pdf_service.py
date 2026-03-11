import os
from sqlalchemy.orm import Session
from app.models.document import Document
from app.models.case import Case
from datetime import datetime, timezone
import pdfplumber
from app.services.classifier import classifier  # 新增導入

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
    def save_pdf_to_db(db: Session, case_id: int, file_path: str, filename: str):
        """抓文字、分類、算期限、存資料庫"""
        # 確認 Case 是否存在
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise ValueError(f"Case id {case_id} not found")

        # 抓文字
        text = PDFService.extract_text_from_pdf(file_path)
        
        # 用規則引擎處理
        process_result = classifier.process_document(text, datetime.now())

        # 建立 Document（包含分類結果）
        document = Document(
            case_id=case_id,
            filename=filename,
            file_path=file_path,
            uploaded_at=datetime.now(timezone.utc),
            text_content=text,
            doc_type=process_result["doc_type"],
            extracted_data=process_result["extracted_data"],
            deadline=process_result["deadline"],
            deadline_days=process_result["deadline_days"]
        )

        # 存入資料庫
        db.add(document)
        db.commit()
        db.refresh(document)
        return document