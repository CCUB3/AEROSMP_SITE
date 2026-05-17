from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from dotenv import load_dotenv
from jose import jwt, JWTError
import sqlite3
import os

load_dotenv()

app = FastAPI()

ENDPOINT = ("/api/")
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

# ----------- УТИЛИТЫ

def create_token():
    """Создаём токен. Можно добавить expiry, но пока без него."""
    return jwt.encode({"role": "admin"}, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Эта функция будет вызываться автоматически на защищённых роутах."""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="нахуй")
    except JWTError:
        raise HTTPException(status_code=403, detail="токен кривой")

# ------------- РОУТЫ

@app.get(ENDPOINT + "news")  # публичный, без защиты
def get_news():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r["id"], "title": r["title"], "text": r["content"], "date": r["date"]} for r in rows]

@app.post(ENDPOINT + "check_password")  # публичный, возвращает токен
async def verify_password(data: PasswordRequest):
    if data.password == SECRET_ADMIN_PASSWORD:
        token = create_token()
        return {"status": "ok", "token": token}  # отдаём токен фронту
    raise HTTPException(status_code=403, detail="нахуй")

@app.post(ENDPOINT + "news", dependencies=[Depends(verify_token)])  # ЗАЩИЩЁН
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

@app.delete(ENDPOINT + "news/{news_id}", dependencies=[Depends(verify_token)])  # ЗАЩИЩЁН
def delete_news(news_id: int):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM news WHERE id = ?", (news_id,))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.get(ENDPOINT)
def read_root():
    return {"message": "РАБОТАЕТ ЮХУУ ЕЕЕЕЕ"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)