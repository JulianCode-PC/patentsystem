# tests/test_day2_crud_safe.py

#該檔案透過 API 呼叫去測試你的 FastAPI CRUD 是否正常
#透過 API 呼叫去測試你的 FastAPI CRUD 是否正常
import requests

BASE_URL = "http://127.0.0.1:8000"  # FastAPI server 地址；所有 API 都會用這個 base URL 拼接 endpoint


'''
每次呼叫 API 後會得到 response 物件

用 safe_json 解析成 dict，如果不是 JSON，就直接回傳原始文字

這樣測試過程不會因為非 JSON 回應而崩掉
'''
def safe_json(response):
    """嘗試解析 JSON，如果失敗就回傳原始文字"""
    try:#
        return response.json()
    except Exception:
        return response.text

def test_crud():
    print("==== Day2 CRUD API 測試開始 ====")

    # ------------------
    # 先確認 API server 連線
    # ------------------
    try:
        #嘗試 GET /cases/，看能不能連上 API
        #requests.get: 在程式裡「發送 HTTP GET 請求」到指定的 URL，模擬瀏覽器拿資料的行為
        r = requests.get(f"{BASE_URL}/cases/")
        print("連線測試 status:", r.status_code)

        #連不上就會跳 ConnectionError，測試直接停止，提醒使用者先啟動 uvicorn
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

    #用 POST 呼叫 /cases/，送出 JSON 物件
    #requests.post: 在程式裡「發送 HTTP POST 請求」到指定的 URL，模擬瀏覽器送資料的行為，把新資料送到 API，API 會新增到資料庫
    #json=new_case → 這裡是把資料轉成 JSON 傳給 API
    response = requests.post(f"{BASE_URL}/cases/", json=new_case)
    print("POST /cases/ status:", response.status_code)
    print("POST /cases/ response:", safe_json(response))

    #如果 API 回傳的是 JSON 物件，就抓它的 id；如果不是，就設成 None。
    #目的是安全取得新增案件的 id
    #FastAPI 會把 URL 的數字抓出來，存到 case_id 參數裡
    #每個案件都有自己的 Link
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
    response = requests.get(f"{BASE_URL}/cases/") #和上面差別在，這裡是查詢全部案件，不帶 case_id，因此URL 是 /cases/，而不是 /cases/{case_id}
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
    #對應 FastAPI 裡的：@router.put("/{case_id}")
    response = requests.put(f"{BASE_URL}/cases/{case_id}", json=updated_case)
    print(f"PUT /cases/{case_id} status:", response.status_code)
    print(f"PUT /cases/{case_id} response:", safe_json(response))

    # ------------------
    # 5️⃣ 刪除案件 (DELETE)
    # ------------------
    #向 API 送出 DELETE 請求，對應 FastAPI 裡的：@router.delete("/{case_id}")
    response = requests.delete(f"{BASE_URL}/cases/{case_id}")
    print(f"DELETE /cases/{case_id} status:", response.status_code)

    # 確認刪除
    #再次向同一個 URL 送 GET 請求
    #目的是確認這筆案件已經不在資料庫裡
    response = requests.get(f"{BASE_URL}/cases/{case_id}")
    print(f"確認刪除 GET /cases/{case_id} status:", response.status_code)
    print(f"確認刪除 GET /cases/{case_id} response:", safe_json(response))

    print("==== Day2 CRUD API 測試結束 ====")


if __name__ == "__main__":
    test_crud()