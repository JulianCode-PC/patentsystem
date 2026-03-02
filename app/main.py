from fastapi import FastAPI
from app.database import engine, Base
from app.models import case, document

app = FastAPI(title="Patent Docketing System")

# 建立所有資料表
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Patent System is running!"}