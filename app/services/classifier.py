import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple

class PatentClassifier:
    """專利文件分類與關鍵字抽取規則引擎"""
    
    # 文件類型規則（根據你提供的清單）
    TYPE_RULES = {
        # 1. 申請階段
        "核發申請號通知函": ["核發申請號", "申請號通知", "申請案號"],
        
        # 2. 補正/修正
        "補正通知函": ["補正通知", "修正通知", "補充修正"],
        
        # 3. 不受理處分
        "(準)不受理處分書": ["不受理處分", "準不受理", "不予受理"],
        
        # 4. 不公開處分
        "不公開處分書": ["不公開處分", "不予公開", "保密處分"],
        
        # 5. 審查意見
        "審查意見通知函": ["審查意見", "審查意見通知", "Office Action"],
        
        # 6. 初審核准
        "(初審)核准審定書": ["初審核准", "核准審定", "准予專利"],
        
        # 7. 初審核駁
        "(初審)核駁審定書": ["初審核駁", "核駁審定", "核駁理由"],
        
        # 8. 再審查核准
        "再審查核准審定書": ["再審查核准", "再審准予", "再審查審定核准"],
        
        # 9. 再審查核駁
        "再審查核駁審定書": ["再審查核駁", "再審駁回", "再審查審定核駁"],
        
        # 10. 訴願
        "訴願決定書": ["訴願決定", "訴願書", "訴願駁回", "訴願撤銷"],
        
        # 11. 行政訴訟第一審
        "行政訴訟第一審判決": ["行政訴訟", "第一審判決", "一審判決", "地方法院行政訴訟"],
        
        # 12. 行政訴訟上訴審
        "行政訴訟上訴審判決": ["上訴審判決", "二審判決", "高等行政法院", "最高行政法院"],
    }
    
    # 期限規則（你可以根據實際法規調整天數）
    DEADLINE_RULES = {
    # 申請階段
    "核發申請號通知函": 0,              # 僅通知，無期限
    
    # 補正/程序審查
    "補正通知函": 60,                    # 程序補正60天（一般實務）
    "(準)不受理處分書": 30,              # 申復30天
    "不公開處分書": 30,                  # 申復30天
    
    # 實體審查階段
    "審查意見通知函": 60,                 # 申復60天（一般實務）
    
    # 初審核准 ✅ 流程圖第3點：審定書送達後3個月內繳費
    "(初審)核准審定書": 90,               # 3個月 = 90天
    
    # 初審核駁 ✅ 流程圖第4點：審定書送達後2個月提起再審查
    "(初審)核駁審定書": 60,               # 2個月 = 60天
    
    # 再審查核准
    "再審查核准審定書": 60,               # 繳費領證60天（實務）
    
    # 再審查核駁 ✅ 流程圖第5點：審定書送達後30日內提起行政救濟
    "再審查核駁審定書": 30,               # 30天
    
    # 訴願階段 ✅ 流程圖第5點：30日內
    "訴願決定書": 30,                     # 行政訴訟30天
    
    # 行政訴訟階段
    "行政訴訟第一審判決": 30,              # 上訴30天
    "行政訴訟上訴審判決": 0,               # 確定，無期限
    }

    
    # 日期格式規則（民國年自動轉換）
    DATE_PATTERNS = [
        # 中華民國113年3月15日
        (r'中華民國\s*(\d{2,3})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日', 
         lambda m: datetime(int(m.group(1)) + 1911 if int(m.group(1)) < 1000 else int(m.group(1)), 
                          int(m.group(2)), int(m.group(3)))),
        # 113年3月15日
        (r'(\d{2,3})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日',
         lambda m: datetime(int(m.group(1)) + 1911 if int(m.group(1)) < 1000 else int(m.group(1)), 
                          int(m.group(2)), int(m.group(3)))),
        # 2024/3/15
        (r'(\d{4})/(\d{1,2})/(\d{1,2})',
         lambda m: datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))),
    ]
    
    # 🔥 強化版欄位抽取規則（只改這裡！）
    FIELD_RULES = {
        "application_number": [
            
            r'申請[號碼][：:]\s*([A-Z0-9\-]+)',
            r'申請案號[：:]\s*([A-Z0-9\-]+)',
            r'([A-Z]{2}[0-9]{8,})',
            
            
            r'第\s*([A-Z0-9\-]+)\s*號',
            r'申請案號數[：:]\s*([A-Z0-9\-]+)',
            


            r'第\s*([A-Z0-9\-]+)\s*號',
            r'編為第[」"“]?([A-Z0-9\-]+)[」"“]?號',
        ],
        
        # 其他規則完全不變
        "publication_number": [
            r'公告[號碼][：:]\s*([A-Z0-9\-]+)',
            r'公開[號碼][：:]\s*([A-Z0-9\-]+)',
        ],
        "applicant": [
            r'申請人[：:]\s*([^\n]+)',
            r'申請權人[：:]\s*([^\n]+)',
            r'專利權人[：:]\s*([^\n]+)',
            r'正本[：:]\s*([^（\n]+)',
            r'正本[：:]\s*([^\n]+)',
        ],
        "invention_title": [
            # 標準格式
            r'發明名稱[：:]\s*([^\n]+)',
            r'新型名稱[：:]\s*([^\n]+)',
            r'設計名稱[：:]\s*([^\n]+)',
            r'專利名稱[：:]\s*([^\n]+)',
            
            # 🔥 新增：本案「XXX」
            r'本案[「""]?([^「」\n]+)[」""]?',
            
            # 🔥 新增：括號裡的內容
            r'[（(]([^）)]+)[）)]',
            
            # 最後手段：抓第一行看起來像名稱的
            r'^([^\n]{5,30})$',
        ],
        "decision_date": [  # 處分/審定日期
            r'審定日期[：:]\s*([^ \n]+)',
            r'處分日期[：:]\s*([^ \n]+)',
            r'判決日期[：:]\s*([^ \n]+)',
        ]
    }

    @classmethod
    def classify(cls, text: str) -> str:
        """判斷文件類型（完整12種）"""
        if not text:
            return "未知類型"
        
        # 優先判斷最特定的類型
        for doc_type, keywords in cls.TYPE_RULES.items():
            for keyword in keywords:
                if keyword in text:
                    return doc_type
                    
        # 沒匹配到
        return "未知類型"

    @classmethod
    def extract_dates(cls, text: str) -> Dict[str, str]:
        """抽出文件中所有重要日期"""
        dates = {}
        
        # 找申請日
        for pattern, parser in cls.DATE_PATTERNS:
            # 申請日
            match = re.search(r'申請[日號].{0,10}' + pattern, text)
            if match:
                try:
                    date = parser(match)
                    dates["filing_date"] = date.isoformat()
                    break
                except:
                    pass
        
        # 找發文日/處分日
        for pattern, parser in cls.DATE_PATTERNS:
            match = re.search(r'(發文日|處分日|審定日).{0,10}' + pattern, text)
            if match:
                try:
                    date = parser(match)
                    dates["decision_date"] = date.isoformat()
                    break
                except:
                    pass
        
        return dates

    @classmethod
    def extract_fields(cls, text: str) -> Dict[str, Any]:
        """抽出關鍵欄位（強化版）"""
        extracted = {}
        
        for field, patterns in cls.FIELD_RULES.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    value = match.group(1).strip()
                    
                    # 🔥 新增：過濾掉「名稱：」這類前綴
                    if field == "applicant":
                        # 如果值是「名稱：xxx」，只取 xxx
                        if value.startswith("名稱：") or value.startswith("名稱:"):
                            value = value[3:].strip()
                        elif "名稱：" in value or "名稱:" in value:
                            # 處理「名稱：國立屏東科技大學」這種
                            parts = re.split(r'名稱[：:]', value)
                            if len(parts) > 1:
                                value = parts[1].strip()
                    
                    # 只存非空值
                    if value:
                        extracted[field] = value
                        break  # 找到第一個就跳出
        
        return extracted

    @classmethod
    def calculate_deadline(cls, doc_type: str, received_date: datetime = None) -> Tuple[Optional[datetime], int]:
        """計算截止日"""
        if not received_date:
            received_date = datetime.now()
            
        days = cls.DEADLINE_RULES.get(doc_type, 0)
        if days > 0:
            return received_date + timedelta(days=days), days
        return None, 0

    @classmethod
    def process_document(cls, text: str, received_date: datetime = None) -> Dict[str, Any]:
        """完整處理文件"""
        # 分類
        doc_type = cls.classify(text)
        
        # 抽欄位
        fields = cls.extract_fields(text)
        
        # 抽日期
        dates = cls.extract_dates(text)
        
        # 算期限
        deadline, days = cls.calculate_deadline(doc_type, received_date)
        
        return {
            "doc_type": doc_type,
            "extracted_data": {
                "fields": fields,
                "dates": dates
            },
            "deadline": deadline.isoformat() if deadline else None,
            "deadline_days": days
        }

# 建立實例
classifier = PatentClassifier()