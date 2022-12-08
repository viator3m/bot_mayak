import sqlite3


def db_init():
    """Создает базу данных и таблицу."""
    con = sqlite3.connect('db.sqlite', check_same_thread=False)
    cur = con.cursor()

    cur.executescript('''
        CREATE TABLE IF NOT EXISTS urls(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER NOT NULL,
        name VARCHAR(100) NOT NULL,
        url VARCHAR(100) NOT NULL,
        xpath VARCHAR(100) NOT NULL
        );
    ''')

    return con, cur


def insert_to_db(con, cur, data):
    """Вставляет полученные данные в БД."""
    cur.executemany('INSERT INTO urls VALUES(null,?, ?, ?, ?);', data)
    con.commit()
