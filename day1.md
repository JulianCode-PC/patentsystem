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



| 檔案              | 主要功能                                                        |
| --------------- | ----------------------------------------------------------- |
| **database.py** | 資料庫設定：建立 `engine`, `SessionLocal`, `Base`，提供路由用的 `get_db()` |
| **case.py**     | ORM 模型：定義 `Case` table 及欄位，跟 Document 建立一對多關聯               |
| **document.py** | ORM 模型：定義 `Document` table 及欄位，連回 Case                      |
| **main.py**     | 啟動 FastAPI app，初始化資料庫，註冊路由或簡單首頁                             |


🔹 2️⃣ 四個檔案的連接方式

database.py → 提供基底和 session

Case 和 Document 都繼承 Base

SessionLocal() 提供資料庫操作工具

case.py / document.py → ORM 模型

兩個檔案各自定義資料表欄位

Document 用 ForeignKey 連回 Case

Case 用 relationship 連回多個 Document

main.py → 啟動點

匯入 Base、模型 (Case, Document)

呼叫 Base.metadata.create_all(bind=engine) → SQLAlchemy 根據模型建立資料表

啟動 FastAPI server → 提供 API



執行流程

1.啟動 FastAPI
uvicorn app.main:app --reload
→ Python 執行 main.py

2.main.py 讀取 database.py
取得 engine 與 Base
初始化資料庫連線工具

3.main.py 匯入 ORM 模型
from app.models.case import Case
from app.models.document import Document

SQLAlchemy 知道每個 table 有哪些欄位與關聯

4.建立資料表

Base.metadata.create_all(bind=engine)

根據模型在 MySQL 建立 cases 和 documents table（如果還沒存在）

5.啟動 FastAPI server

你可以透過瀏覽器或 API 工具存取：

GET http://127.0.0.1:8000/

返回：

{"message": "Patent System is running!"}

6.使用資料庫

Route 要操作 DB 時：

db = SessionLocal()  # 從 database.py 取得 session
db.add(new_case)
db.commit()
db.close()



實務建立檔案的順序

database.py 先建

所有模型都要繼承同一個 Base，

也要用同一個 engine 連線資料庫。
→ 所以最先建立。

先建父表（Case）

有外鍵關聯時，父表必須先建立，否則 MySQL 會報錯。

子表 (Document) 才能指向父表。

再建子表（Document）

ForeignKey 依賴父表存在

SQLAlchemy 會正確建立關聯

main.py 最後

這個檔案是啟動點

會 import 所有模型、呼叫 Base.metadata.create_all()

啟動 FastAPI server

測試

啟動 server、打 API 測試，資料表才會真的在 MySQL 建好