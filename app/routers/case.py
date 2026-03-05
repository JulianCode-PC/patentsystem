from fastapi import APIRouter

router = APIRouter(prefix="/cases", tags=["cases"])

# 測試 CRUD 路徑
@router.get("/")
def get_cases():
    return {"message": "List all cases"}

@router.post("/")
def create_case():
    return {"message": "Create a case"}