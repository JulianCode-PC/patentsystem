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

💡 設計理念：
分層：API 路由 → 服務層 → 資料庫模型

可維護：不同功能放不同資料夾，例如 models 只存放資料庫表格，routers 只負責 URL 路由

模組化：未來如果增加更多表格或功能，只要在 models / services / routers 新增即可，不會打亂原本架構