from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from dotenv import load_dotenv
from jose import jwt, JWTError
from fastapi.staticfiles import StaticFiles
import sqlite3
import os

load_dotenv()

app = FastAPI()

ENDPOINT = ("/")
SECRET_ADMIN_PASSWORD = os.getenv("SECRET_ADMIN_PASSWORD")
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------- МОДЕЛЬКИ
class PasswordRequest(BaseModel):
    password: str

class NewsItem(BaseModel):
    title: str
    content: str
    date: str

class RuleItem(BaseModel):
    title: str
    content: str
    order_num: int = 0


# ----------- УТИЛИТЫ
def create_token():
    return jwt.encode({"role": "admin"}, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="нахуй")
    except JWTError:
        raise HTTPException(status_code=403, detail="токен кривой")


# ------------- РОУТЫ: АВТОРИЗАЦИЯ
@app.post(ENDPOINT + "check_password")
async def verify_password(data: PasswordRequest):
    if data.password == SECRET_ADMIN_PASSWORD:
        return {"status": "ok", "token": create_token()}
    raise HTTPException(status_code=403, detail="нахуй")


# ------------- РОУТЫ: НОВОСТИ
@app.get(ENDPOINT + "news")
def get_news():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r["id"], "title": r["title"], "text": r["content"], "date": r["date"]} for r in rows]

@app.post(ENDPOINT + "news", dependencies=[Depends(verify_token)])
def add_news(item: NewsItem):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS news
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, date TEXT)''')
    cursor.execute("INSERT INTO news (title, content, date) VALUES (?, ?, ?)",
                   (item.title, item.content, item.date))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.delete(ENDPOINT + "news/{news_id}", dependencies=[Depends(verify_token)])
def delete_news(news_id: int):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM news WHERE id = ?", (news_id,))
    conn.commit()
    conn.close()
    return {"status": "success"}


# ------------- РОУТЫ: ПРАВИЛА (вайбкоооод) !проверено мной!
@app.get(ENDPOINT + "rules")
def get_rules():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rules ORDER BY order_num ASC, id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r["id"], "title": r["title"], "content": r["content"], "order_num": r["order_num"]} for r in rows]

@app.post(ENDPOINT + "rules", dependencies=[Depends(verify_token)])
def add_rule(item: RuleItem):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS rules
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, order_num INTEGER DEFAULT 0)''')
    cursor.execute("INSERT INTO rules (title, content, order_num) VALUES (?, ?, ?)",
                   (item.title, item.content, item.order_num))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.put(ENDPOINT + "rules/{rule_id}", dependencies=[Depends(verify_token)])
def update_rule(rule_id: int, item: RuleItem):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    result = cursor.execute(
        "UPDATE rules SET title = ?, content = ?, order_num = ? WHERE id = ?",
        (item.title, item.content, item.order_num, rule_id)
    )
    conn.commit()
    conn.close()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Правило не найдено")
    return {"status": "success"}

@app.delete(ENDPOINT + "rules/{rule_id}", dependencies=[Depends(verify_token)])
def delete_rule(rule_id: int):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM rules WHERE id = ?", (rule_id,))
    conn.commit()
    conn.close()
    return {"status": "success"}


# ------------- СЛУЖЕБНЫЙ
@app.get(ENDPOINT)
def read_root():
    return {"message": "РАБОТАЕТ ЮХУУ ЕЕЕЕЕ"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)