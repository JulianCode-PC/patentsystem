| import                | 作用                      |
| --------------------- | ----------------------- |
| APIRouter             | 建立路由集合                  |
| Depends               | 注入依賴（例如 DB session）     |
| HTTPException         | 回傳 HTTP 錯誤              |
| Session               | SQLAlchemy DB session   |
| List                  | 回傳多筆資料                  |
| get_db                | 提供 DB session           |
| Case                  | ORM 模型（資料表）             |
| CaseCreate/Update/Out | Pydantic schema，驗證輸入/回傳 |
