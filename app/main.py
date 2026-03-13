from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse  # 加上這行！
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.models import case, document
from app.routers import case as case_router
from app.routers import document as document_router
from app.routers import case_page

app = FastAPI(title="Patent Docketing System")

app.include_router(case_page.router)
app.include_router(case_router.router)
app.include_router(document_router.router)

templates = Jinja2Templates(directory="templates")
Base.metadata.create_all(bind=engine)

# 🔥 修改這裡：直接導向儀表板
@app.get("/", response_class=RedirectResponse)
def home():
    return RedirectResponse(url="/cases")