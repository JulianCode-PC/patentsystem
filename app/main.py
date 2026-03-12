from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.models import case, document
from app.routers import case as case_router
from app.routers import document as document_router
from app.routers import case_page

app = FastAPI(title="Patent Docketing System")

# 🔥 順序很重要：頁面路由先！
app.include_router(case_page.router)        # HTML 頁面
app.include_router(case_router.router)      # JSON API
app.include_router(document_router.router)  # JSON API

templates = Jinja2Templates(directory="templates")
Base.metadata.create_all(bind=engine)

@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    from app.models.case import Case
    cases = db.query(Case).all()
    return templates.TemplateResponse("index.html", {"request": request, "cases": cases})