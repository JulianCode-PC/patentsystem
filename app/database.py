# create_engine是sqlalchemy裡的函數 → 建立python跟資料庫連線的橋樑
from sqlalchemy import create_engine

# 導入 SQLAlchemy ORM（物件關聯對映）的兩個核心工具，sessionmaker 和 declarative_base。
# sessionmaker → 建立一個 Session 工廠，用來跟資料庫互動（CRUD：新增、查詢、修改、刪除）。
# declarative_base → 建立一個 基底類別 Base，使得可以用 Python 類別定義資料表。
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# 🔥 改成 SQLite 連線字串
# SQLite 不需要帳號密碼，資料會存在專案目錄下的 patent.db 檔案
DATABASE_URL = "sqlite:///./patent.db"

# 建立資料庫引擎 engine：
# engine 是 SQLAlchemy 與資料庫溝通的橋樑，echo=True → 開發模式，執行 SQL 時會印出 SQL 指令，方便 debug
# DATABASE_URL指定資料庫類型與位置
# 建立 engine 後，就可以建立資料表、執行 SQL 指令等操作
# engine 是 資料庫的「引擎」，它本身不會立刻建立真實連線。
# 🔥 SQLite 需要加上 connect_args 來支援多執行緒
engine = create_engine(
    DATABASE_URL, 
    echo=True,
    connect_args={"check_same_thread": False}  # SQLite 專用設定
)

# 建立 SessionLocal → 每次操作資料庫時使用
# autocommit=False → 變更資料庫時需要手動 commit
# autoflush=False → 不會自動刷新
# bind=engine → 指定使用剛剛建立的 engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# declarative_base 確實是一個函數，
# 在 SQLAlchemy 裡的作用是 生成一個「基底類別」，這個類別本身是用來讓你定義 ORM 類別（對應資料表）的父類
Base = declarative_base()

# 在 FastAPI 裡常用來當依賴（dependency）
# 建立一個資料庫 Session，提供給使用者使用，使用完後自動關閉連線
def get_db():
    # 這裡建立了一個 資料庫 Session，也就是跟資料庫的連線
    # SessionLocal() 是用 sessionmaker(bind=engine) 創建的 Session 工廠
    # Session 是真正跟資料庫互動的「工作單位」，會從 engine 池裡取得真實連線，
    db = SessionLocal()
    try:
        # yield 讓函數變成 generator。在 FastAPI 裡，這意味著：路由可以「拿到這個 session 使用」
        # 路由程式跑完之後，控制權會回到這個函數。
        yield db
    finally:
        # 無論路由執行成功或發生例外，都會執行 db.close()。
        # 釋放資料庫連線，避免連線洩漏
        db.close()

'''
database.py 的作用：

負責 設定資料庫連線、建立 ORM 基底、提供資料庫操作的 session。

1.告訴 Python 你的資料庫在哪裡(DATABASE_URL) → 現在是 SQLite 檔案
2.建立 SQLAlchemy 的 engine → 讓程式可以跟 SQLite 連線 (engine)
3.建立 SessionLocal → 每次操作資料庫時使用 (SessionLocal)
4.建立 Base → 所有 ORM 模型都要繼承它 (Base)
5.提供 get_db() → 路由中方便取得資料庫 session

🔥 SQLite 版特色：
- 不用安裝 MySQL
- 不用設定帳號密碼
- 所有資料存在 patent.db 檔案
- 移植方便，複製檔案就好
''' 