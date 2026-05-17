import sqlite3

#создаем файл базы данных
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

#создаем таблицу
cursor.execute('''
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        date TEXT NOT NULL
    )
''')

#очищаем таблицу перед записью
cursor.execute('DELETE FROM news')

#стартовые новости
news_data = [
    ("Выборы президента", "Президентом нашего сервера стал romchik656", "12 Мая"),
    ("Крафт Гироскопа", "Усложнили крафт гироскопа для баланса", "12 Мая"),
]

#вставляем данные в таблицу
cursor.executemany('INSERT INTO news (title, content, date) VALUES (?, ?, ?)', news_data)

#сохраняем изменения и закрываем базу
conn.commit()
conn.close()

print("База данных готова")