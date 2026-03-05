'''
整個系統的"entry point"


1.建立 FastAPI 應用程式
2.連接資料庫
3.建立資料表
4.提供基本 API 路由
5.作為 uvicorn 啟動的入口
'''
#用來建立 API 伺服器
from fastapi import FastAPI
#匯入在database.py裡定義的 engine、Base
from app.database import engine, Base
#讓 Python 讀取這兩個 model 檔案
#如果沒 import，create_all() 會找不到表，什麼都不會建立。
from app.models import case, document
from app.routers import case 


#http://127.0.0.1:8000/docs
#在 FastAPI 專案裡，
#app = FastAPI(...) 這個物件只需要建立一次，代表FastAPI 的入口物件
app = FastAPI(title="Patent Docketing System") 


app.include_router(case.router)

#根據所有繼承 Base 的 class，自動建立資料表
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Patent System is running!"}

