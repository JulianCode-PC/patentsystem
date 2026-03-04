patent_system/
│
├── app/                 # 主要程式碼
│   ├── main.py          # FastAPI 入口，啟動 Server
│   ├── database.py      # 資料庫連線與 Session 設定
│   ├── models/          # ORM 模型 (資料庫表格映射)
│   │   ├── case.py
│   │   └── document.py
│   ├── routers/         # API 路由 (後續放 CRUD 路徑)
│   ├── services/        # 業務邏輯 (複雜處理放這)
│   └── schemas/         # Pydantic 模型，用於 request/response
│
├── uploads/             # 上傳檔案存放
├── requirements.txt     # 套件依賴清單
└── venv/                # Python 虛擬環境



Day1 — 架構與資料庫連線

理解資料庫、ORM、Session 的概念

把資料表模型（Case / Document）設計好

要讓 FastAPI server 能啟動、能連上 MySQL


模組化：未來如果增加更多表格或功能，只要在 models / services / routers 新增即可，不會打亂原本架構


database.py → 建立 ORM 環境
case.py → 定義 cases 表
document.py → 定義 documents 表
main.py → 啟動系統
router → 操作資料