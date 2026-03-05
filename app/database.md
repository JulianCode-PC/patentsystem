1️⃣ 關鍵字 / SQLAlchemy 核心功能

| 名稱              | 類型                    | 功能                              |
| --------------- | --------------------- | ------------------------------- |
| `Column`        | SQLAlchemy class      | 定義資料表欄位                         |
| `Integer`       | SQLAlchemy type       | 整數欄位                            |
| `String`        | SQLAlchemy type       | 字串欄位，`String(1000)` 表示最多 1000 字 |
| `ForeignKey`    | SQLAlchemy class      | 設定外鍵，建立表間關聯                     |
| `relationship`  | SQLAlchemy ORM        | 定義 ORM 物件間的關聯（不會建立欄位，只是方便程式操作）  |
| `Base`          | ORM 基底類別              | 所有 ORM 類別都要繼承它，提供 metadata 管理   |
| `__tablename__` | 類屬性 (class attribute) | 指定資料表名稱（必填）                     |


2️⃣ 變數 / ORM 類別欄位
在 Document 類別裡，每個變數其實對應 資料表欄位，或 ORM 物件關聯：
| 變數名稱        | 類型 / 關聯                                          | 作用                                   |
| ----------- | ------------------------------------------------ | ------------------------------------ |
| `id`        | Column(Integer, primary_key=True, index=True)    | 主鍵，自動唯一識別每筆文件，建立索引加快查詢               |
| `case_id`   | Column(Integer, ForeignKey("cases.id"))          | 外鍵，對應 `Case` 的 id，建立「文件屬於哪個案件」的關聯    |
| `filename`  | Column(String(1000))                             | 儲存檔案名稱                               |
| `file_path` | Column(String(1000))                             | 儲存檔案在伺服器的路徑                          |
| `case`      | relationship("Case", back_populates="documents") | ORM 雙向關聯，方便從 `Document` 取得對應的 `Case` |


3️⃣ 變數從哪來

資料表欄位：每個欄位對應你想在資料庫存的資料（例如 id, filename, file_path, case_id）
關聯欄位：case 是 ORM 層面的「連結」，方便程式用物件操作資料庫，不必寫 SQL JOIN
額外設定：像 primary_key=True、index=True、ForeignKey("cases.id") 都是資料庫層面的額外規則