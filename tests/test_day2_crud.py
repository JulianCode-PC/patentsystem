# tests/test_day2_crud_safe.py
import requests

BASE_URL = "http://127.0.0.1:8000"  # API 根路徑，注意不要加 /docs

def safe_json(response):
    """嘗試解析 JSON，如果失敗就回傳原始文字"""
    try:
        return response.json()
    except Exception:
        return response.text

def test_crud():
    print("==== Day2 CRUD API 測試開始 ====")

    # ------------------
    # 先確認 API server 連線
    # ------------------
    try:
        r = requests.get(f"{BASE_URL}/cases/")
        print("連線測試 status:", r.status_code)
    except requests.exceptions.ConnectionError:
        print("無法連線到 API server，請先啟動 uvicorn")
        return

    # ------------------
    # 1️⃣ 新增案件 (POST)
    # ------------------
    new_case = {
        "title": "測試案件",
        "description": "這是一個 Day2 CRUD 測試案件",
        
    }
    response = requests.post(f"{BASE_URL}/cases/", json=new_case)
    print("POST /cases/ status:", response.status_code)
    print("POST /cases/ response:", safe_json(response))
    case_id = safe_json(response).get("id") if isinstance(safe_json(response), dict) else None
    if not case_id:
        print("新增案件失敗，無法繼續測試")
        return

    # ------------------
    # 2️⃣ 查詢單一案件 (GET)
    # ------------------
    response = requests.get(f"{BASE_URL}/cases/{case_id}")
    print(f"GET /cases/{case_id} status:", response.status_code)
    print(f"GET /cases/{case_id} response:", safe_json(response))

    # ------------------
    # 3️⃣ 查詢所有案件 (GET)
    # ------------------
    response = requests.get(f"{BASE_URL}/cases/")
    print("GET /cases/ status:", response.status_code)
    print("GET /cases/ response:", safe_json(response))

    # ------------------
    # 4️⃣ 修改案件 (PUT)
    # ------------------
    updated_case = {
        "title": "修改後的測試案件",
        "description": "已經修改的描述",
        "status": "closed"
    }
    response = requests.put(f"{BASE_URL}/cases/{case_id}", json=updated_case)
    print(f"PUT /cases/{case_id} status:", response.status_code)
    print(f"PUT /cases/{case_id} response:", safe_json(response))

    # ------------------
    # 5️⃣ 刪除案件 (DELETE)
    # ------------------
    response = requests.delete(f"{BASE_URL}/cases/{case_id}")
    print(f"DELETE /cases/{case_id} status:", response.status_code)

    # 確認刪除
    response = requests.get(f"{BASE_URL}/cases/{case_id}")
    print(f"確認刪除 GET /cases/{case_id} status:", response.status_code)
    print(f"確認刪除 GET /cases/{case_id} response:", safe_json(response))

    print("==== Day2 CRUD API 測試結束 ====")


if __name__ == "__main__":
    test_crud()