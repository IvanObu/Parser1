import sqlite3
from Sites_parsers.main_pars import Pars_All1, Pars_All2, Pars_All3
from Sicret import categories
from datetime import datetime, timedelta



def create_tables(conn):
    """Создает таблицы, если их нет"""
    cursor = conn.cursor()
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model TEXT NOT NULL,
        category TEXT NOT NULL,
        store TEXT NOT NULL,
        UNIQUE(model, store)
    );

    CREATE TABLE IF NOT EXISTS prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        price INTEGER NOT NULL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id)
    );

    CREATE TABLE IF NOT EXISTS availability (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        in_stock BOOLEAN NOT NULL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id)
    );
    """)
    conn.commit()


def save_product(conn, model, category, store, price, in_stock):
    """Сохраняем товар в БД и обновляем цену/наличие"""
    cursor = conn.cursor()

    # Проверяем, есть ли товар
    cursor.execute("SELECT id FROM products WHERE model = ? AND store = ?", (model, store))
    product = cursor.fetchone()

    if not product:
        cursor.execute("INSERT INTO products (model, category, store) VALUES (?, ?, ?)",
                       (model, category, store))
        conn.commit()
        product_id = cursor.lastrowid
    else:
        product_id = product[0]

    # Проверяем, изменилась ли цена
    cursor.execute("SELECT price FROM prices WHERE product_id = ? ORDER BY date DESC LIMIT 1", (product_id,))
    last_price = cursor.fetchone()

    if not last_price or last_price[0] != price:
        cursor.execute("INSERT INTO prices (product_id, price) VALUES (?, ?)", (product_id, price))
        conn.commit()

    # Обновляем наличие
    cursor.execute("INSERT INTO availability (product_id, in_stock) VALUES (?, ?)", (product_id, in_stock))
    conn.commit()


def parse_and_save(conn):
    """Парсим данные и сохраняем в БД"""
    create_tables(conn)  # Убеждаемся, что таблицы есть

    for category, urls in categories.items():
        url1, url2, url3 = urls

        for product in Pars_All1(category, url1, find_all=0):
            price = product["Цена"].replace(" ", "")
            price = int(price) if price.isdigit() else price
            save_product(conn, product["Модель"], category, "Магазин 1", price, product["Наличие"] == "В наличии")

        for product in Pars_All2(category, url2, find_all=0):
            price = product["Цена"].replace(" ", "")
            price = int(price) if price.isdigit() else price
            save_product(conn, product["Модель"], category, "Магазин 2", price, product["Наличие"] == "В наличии")

        for product in Pars_All3(url3):
            price = product["Цена"].replace(" ", "")
            price = int(price) if price.isdigit() else price
            save_product(conn, product["Модель"], category, "Магазин 3", price, product["Наличие"] == "В наличии")

def cleanup_old_prices(conn):
    """Удаляет записи о ценах и наличии, которым более 6 месяцев"""
    cursor = conn.cursor()
    six_months_ago = datetime.now() - timedelta(days=180)

    cursor.execute("DELETE FROM prices WHERE date < ?", (six_months_ago,))
    cursor.execute("DELETE FROM availability WHERE date < ?", (six_months_ago,))

    conn.commit()
    print("Старые записи успешно удалены.")