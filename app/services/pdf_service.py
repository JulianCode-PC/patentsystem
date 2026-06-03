import os
import re
import pdfplumber
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from typing import Tuple, Optional

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
    def extract_decision_date(text: str) -> Optional[datetime]:
        """手動從文字中抓取發文日期"""
        # 模式1: 發文日期：中華民國114年10月21日
        pattern1 = r'發文日期[：:]\s*中華民國\s*(\d{2,3})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日'
        match = re.search(pattern1, text)
        if match:
            year = int(match.group(1)) + 1911
            month = int(match.group(2))
            day = int(match.group(3))
            print(f"✅ 模式1抓到: {year}-{month}-{day}")
            return datetime(year, month, day)
        
        # 模式2: 發文日期：114年10月21日
        pattern2 = r'發文日期[：:]\s*(\d{2,3})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日'
        match = re.search(pattern2, text)
        if match:
            year = int(match.group(1))
            if year < 100:
                year += 1911
            month = int(match.group(2))
            day = int(match.group(3))
            print(f"✅ 模式2抓到: {year}-{month}-{day}")
            return datetime(year, month, day)
        
        # 模式3: 發文日期：2025/10/21
        pattern3 = r'發文日期[：:]\s*(\d{4})/(\d{1,2})/(\d{1,2})'
        match = re.search(pattern3, text)
        if match:
            print(f"✅ 模式3抓到: {match.group(1)}-{match.group(2)}-{match.group(3)}")
            return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        
        print("⚠️ 未抓到發文日期")
        return None

    @staticmethod
    def save_pdf_to_db(db: Session, file_path: str, filename: str, case_id: Optional[int] = None) -> Tuple[Document, Case]:
        """
        抓文字、分類、找案件、存資料庫
        回傳: (Document, Case)
        """
        # 1. 抓文字
        text = PDFService.extract_text_from_pdf(file_path)
        
        # 2. 用規則引擎處理
        result = classifier.process_document(text)
        
        # 3. 手動抓取發文日期（因為 classifier 可能抓不到）
        decision_date = PDFService.extract_decision_date(text)
        if decision_date:
            print(f"✅ 手動抓到發文日期: {decision_date}")
            
            # 🔥 確保 extracted_data 有 dates 欄位
            if "dates" not in result["extracted_data"]:
                result["extracted_data"]["dates"] = {}
            result["extracted_data"]["dates"]["decision_date"] = decision_date.isoformat()
            
            # 重新計算期限（用發文日期）
            doc_type = result["doc_type"]
            days = classifier.DEADLINE_RULES.get(doc_type, 0)
            if days > 0:
                deadline = decision_date + timedelta(days=days)
                result["deadline"] = deadline
                result["deadline_days"] = days
                print(f"✅ 使用發文日期計算截止日: {deadline.date()}")
            else:
                print(f"⚠️ 文件類型 {doc_type} 無期限規則")
        else:
            print(f"⚠️ 未抓到發文日期，使用 classifier 的結果")
        
        # 4. 從結果取得申請案號和專利名稱
        fields = result["extracted_data"].get("fields", {})
        app_number = fields.get("application_number")
        title = fields.get("invention_title", "新專利案件")
        applicant = fields.get("applicant", "")
        
        # 5. 用申請案號找或建立 Case
        case = None
        if case_id is not None:
            case = db.query(Case).filter(Case.id == case_id).first()
            if not case:
                raise ValueError("案件不存在")
        elif app_number:
            case = db.query(Case).filter(Case.case_no == app_number).first()
        
        if not case:
            case = Case(
                case_no=app_number or f"TEMP{datetime.now().strftime('%Y%m%d%H%M%S')}",
                title=title,
                applicant=applicant,
                status="進行中",
                patent_type="發明專利"
            )
            db.add(case)
            db.commit()
            db.refresh(case)
        
        # 6. 建立 Document
        deadline_value = result.get("deadline")
        if isinstance(deadline_value, str):
            deadline_value = datetime.fromisoformat(deadline_value)
        
        document = Document(
            case_id=case.id,
            filename=filename,
            file_path=file_path,
            uploaded_at=datetime.now(timezone.utc),
            text_content=text,
            doc_type=result["doc_type"],
            extracted_data=result["extracted_data"],  # 🔥 這裡會包含發文日期
            deadline=deadline_value,
            deadline_days=result.get("deadline_days", 0)
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        return document, case
