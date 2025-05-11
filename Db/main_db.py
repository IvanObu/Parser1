import sqlite3
from Sites_parsers.main_pars import Pars_All1, Pars_All2, Pars_All3
from Secret import categories
from datetime import datetime, timedelta
import re
import json
import os
import asyncio
from aiogram import Bot


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

    CREATE TABLE IF NOT EXISTS my_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    Notice INTEGER,
    FOREIGN KEY (product_id) REFERENCES products(id)
    );
    
    CREATE TABLE IF NOT EXISTS User (
        Name TEXT,
        Us_Id INTEGER UNIQUE NOT NULL
    );
    CREATE TABLE IF NOT EXISTS Settings (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        update_interval_days INTEGER NOT NULL DEFAULT 4
    );
    
    """)
    cursor.execute("INSERT OR IGNORE INTO Settings (id, update_interval_days) VALUES (1, 4)")
    conn.commit()


async def check_and_notify(conn, bot: Bot, USER_ID):
    if not USER_ID:
        print("⚠️ Пустой USER_ID, уведомление не отправлено")
        return

    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT p.id, p.model, p.store
            FROM products p
            JOIN my_list ml ON p.id = ml.product_id
            WHERE ml.Notice = 1
        """)
        products_to_notify = cursor.fetchall()

        if not products_to_notify:
            return

        product_ids = [str(p[0]) for p in products_to_notify]
        cursor.execute(f"""
            SELECT product_id, price, date FROM prices 
            WHERE product_id IN ({','.join(['?'] * len(product_ids))})
            ORDER BY product_id, date DESC
        """, product_ids)

        prices_data = cursor.fetchall()
        prices_dict = {}
        for product_id, price, date in prices_data:
            if product_id not in prices_dict:
                prices_dict[product_id] = []
            prices_dict[product_id].append(price)

        # Формируем и отправляем уведомления
        for product_id, model, store in products_to_notify:
            prices = prices_dict.get(product_id, [])

            if len(prices) >= 2 and prices[0] != prices[1]:
                message = (
                    f"🔔 Цена обновилась:\n"
                    f"📦 {model}\n"
                    f"🏬 Магазин: {store}\n"
                    f"💰 Была: {prices[1]}₽ → Стала: {prices[0]}₽"
                )

                try:
                    await bot.send_message(USER_ID, message)
                except Exception as e:
                    print(f"Ошибка отправки пользователю {USER_ID}: {e}")

    except Exception as e:
        print(f"❌ Ошибка в check_and_notify: {e}")

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


def save_iphones_to_json(iphones_dict, filename="iphones.json", folder="Db"):
    os.makedirs(folder, exist_ok=True)

    serializable_dict = {}
    for series, data in iphones_dict.items():
        serializable_dict[series] = {
            "models": list(data["models"]),
            "memory": {model: list(mem_set) for model, mem_set in data["memory"].items()},
            "colors": {model: list(color_set) for model, color_set in data["colors"].items()}
        }

    filepath = os.path.join(folder, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(serializable_dict, f, ensure_ascii=False, indent=2)

def save_macbooks_to_json(macbooks_dict, filename="macbooks.json", folder="Db"):
    os.makedirs(folder, exist_ok=True)

    serializable_dict = {}
    for series, data in macbooks_dict.items():
        serializable_dict[series] = {
            "models": list(data["models"]),
            "cpu": {model: list(cpu_set) for model, cpu_set in data["cpu"].items()},
            "ram": {model: list(ram_set) for model, ram_set in data["ram"].items()},
            "storage": {model: list(storage_set) for model, storage_set in data["storage"].items()},
            "colors": {model: list(color_set) for model, color_set in data["colors"].items()}
        }

    filepath = os.path.join(folder, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(serializable_dict, f, ensure_ascii=False, indent=2)

IPHONES = {}

def add_to_iphones(series, model, memory, color):
    if series not in IPHONES:
        IPHONES[series] = {"models": set(), "memory": {}, "colors": {}}

    IPHONES[series]["models"].add(model)

    if model not in IPHONES[series]["memory"]:
        IPHONES[series]["memory"][model] = set()
    IPHONES[series]["memory"][model].add(memory)

    if model not in IPHONES[series]["colors"]:
        IPHONES[series]["colors"][model] = set()
    IPHONES[series]["colors"][model].add(color)

MacBooks = {}

def add_to_macbooks(series, model, cpu, ram, storage, color):
    if series not in MacBooks:
        MacBooks[series] = {"models": set(), "cpu": {}, "ram": {}, "storage": {}, "colors": {}}

    MacBooks[series]["models"].add(model)

    for key, val, dic in [("cpu", cpu, MacBooks[series]["cpu"]),
                          ("ram", ram, MacBooks[series]["ram"]),
                          ("storage", storage, MacBooks[series]["storage"]),
                          ("colors", color, MacBooks[series]["colors"])]:
        if model not in dic:
            dic[model] = set()
        dic[model].add(val)

def parse_iphone_info(model_str: str):
    # Нормализуем память
    model_str = re.sub(r"\b(\d+)\s*[ГгГ][БбБ]\b", r"\1GB", model_str)
    model_str = re.sub(r"\b(\d+)\s*[ТтТ][БбБ]\b", r"\1TB", model_str)
    model_str = re.sub(r"\b(\d+)Gb\b", r"\1GB", model_str, flags=re.IGNORECASE)
    model_str = re.sub(r"\b(\d+)Tb\b", r"\1TB", model_str, flags=re.IGNORECASE)
    model_str = model_str.replace("+", "").replace("темно-", "")
    # Убираем Apple
    model_str = model_str.replace("Apple ", "").strip()

    # Ищем память
    memory_match = re.search(r"\b\d+(GB|TB)\b", model_str)
    if not memory_match:
        return None

    memory = memory_match.group(0)
    memory_start = memory_match.start()
    memory_end = memory_match.end()

    left = model_str[:memory_start].strip()
    right = model_str[memory_end:].strip()

    match = re.search(r"iPhone\s+(.+)", left)
    if not match:
        return None

    model_part = match.group(1).strip()
    # Определяем серию
    if model_part.upper().startswith("SE"):
        series = "SE"
    else:
        series_match = re.match(r"(\d{2})", model_part)
        if not series_match:
            return None
        series = series_match.group(1)

    model = model_part
    color = right
    return series, model, memory, color


def parse_mac_info(model_str: str, number):

    model_str = model_str.replace("Apple ", "").strip()

    device_match = re.search(r"(MacBook Air|MacBook Pro|iMac 24|Mac Mini|Mac Studio)", model_str, re.IGNORECASE)
    device_type = device_match.group(1) if device_match else None

    version_match = re.search(r"(MacBook (Air|Pro) \d+|iMac 24|Mac Mini|Mac Studio)", model_str, re.IGNORECASE)
    version = version_match.group(1) if version_match else device_type

    cpu_match = re.search(r'\b(M[1-4])(?:[\s\-]*(Pro|Max|Ultra))?(?:[\s\-]*(Max|Ultra))?\b', model_str, re.IGNORECASE)
    if cpu_match:
        parts = [cpu_match.group(1)]
        if cpu_match.group(2):
            parts.append(cpu_match.group(2).title())
        if cpu_match.group(3):
            parts.append(cpu_match.group(3).title())
        processor = " ".join(parts)
    else:
        processor = None

    ram_match = re.search(r'(\d+)\s*[ГгGg][БbB]', model_str)
    ram = f"{ram_match.group(1)}GB" if ram_match else None

    # Дополнительная проверка на RAM если основной шаблон не сработал
    if ram is None:
        ram_match_alt = re.search(r'RAM[:\s]*(\d+)\s*(GB|ГБ)', model_str, re.IGNORECASE)
        if ram_match_alt:
            ram = f"{ram_match_alt.group(1)}GB"

    memory_matches = re.findall(r'(\d+)\s*([ТтTtГгGg])[БbB]', model_str)
    storage = None
    if len(memory_matches) >= 1:
        raw_storage = f"{memory_matches[-1][0]}{'TB' if memory_matches[-1][1].lower() == 'т' else 'GB'}"
        storage_map = {
            "1024GB": "1TB",
            "2048GB": "2TB",
            "4096GB": "4TB",
            "8192GB": "8TB",
        }
        storage = storage_map.get(raw_storage, raw_storage)

    # Дополнительная проверка на storage если основной шаблон не сработал

    if storage in ["1GB", "2GB"]:
        storage = None

    if storage is None:
        alt_storage = re.search(r'\b(1|2|4|8)\s*ТБ\b', model_str, re.IGNORECASE)
        if alt_storage:
            storage = f"{alt_storage.group(1)}TB"


    color_match = re.search(r'\b(Silver|Space Gray|Green|Blue|Pink|Starlight|Black)\b', model_str, re.IGNORECASE)
    color = color_match.group(1).title() if color_match else None

    if processor is None:
        for val in ['1', '2', '3', '4']:
            if f'M{val}' in model_str or f'М{val}':
                processor = f"M{val}"
                break

    if ram is None:
        model_str.replace("Гб", "ГБ")
        for val in ['8', '16', '24', '32', '36', '64', '96']:
            if f'{val} ГБ' in model_str or f'{val}Gb' in model_str or f'{val} GB' in model_str :
                ram = f"{val}GB"
                break

    if storage is None or storage == "1GB" or storage == "2GB":
        model_str.replace("Гб", "ГБ").replace("Тб", "ТБ")
        for val in ['256', '512', '1024', '2048', '4096', '1', '2']:
            if f' {val} ГБ' in model_str or f' {val}Gb' in model_str:
                storage = f"{val}GB"
                break
            elif f' {val} ТБ' in model_str or f' {val} TB' in model_str or f' {val}TB' in model_str or f' {val}Tb' in model_str:
                storage = f"{val}TB"
                break

    if color is None or "Midnight" in color:
        # print(model_str)
        model_str.replace("желтый", 'Yellow')
        colors = ['Silver', 'Space Gray', 'Black', 'Starlight', 'Blue', 'Pink', 'Purple', 'Green', 'Orange',
                  'Yellow']
        for c in colors:
            if c in model_str:
                color = c
                break
    if storage == "1GB" or storage == "2GB":
        print((device_type, version, processor, ram, storage, color))
        print(model_str)
    if ram is None or storage is None or color is None or processor is None:
        # print((device_type, version, processor, ram, storage, color))
        return
    return (device_type, version, processor, ram, storage, color)

def process_iphone_product(product, category, store_name, conn):

    if "SE" in product["Модель"]:
        product["Модель"] = product["Модель"].replace(" ГБ", "GB").replace("Gb", "GB").replace("(2022)", "2022").replace(",", "")

    product["Модель"] = re.sub(r"\)\s.*", ")", product["Модель"]).replace(" ГБ", "GB").replace("Gb", "GB").replace("(2022)", "2022").replace(",", "")
    product["Модель"] = re.sub(r"\b(Dual Sim|eSIM|nano[- ]?SIM(?:\+eSIM)?|nano SIM\+nano SIM|\+)\b", "",product["Модель"], flags=re.IGNORECASE)
    parsed = parse_iphone_info(product["Модель"])
    if parsed:
        series, model, memory, color = parsed
        add_to_iphones(series, model, memory, color)
    else:
        pass
        print("❌ Не удалось распарсить:", product["Модель"], store_name)
    product["Модель"] = product["Модель"].replace("+", "")
    save_product(conn, product["Модель"], category, store_name, product["Цена"], product["Наличие"] == "В наличии")

def process_mac_product(product, category, store_name, conn):
    model_str = product["Модель"]
    parsed = parse_mac_info(model_str, store_name)
    if parsed:
        series, model, cpu, ram, storage, color = parsed
        add_to_macbooks(series, model, cpu, ram, storage, color)
        save_product(conn, model_str, category, store_name, product["Цена"], product["Наличие"] == "В наличии")
    else:
         print("❌ Не удалось распарсить:", model_str, store_name, "\n")

def parse_and_save(conn):
    """Парсим данные и сохраняем в БД"""
    create_tables(conn)  # Убеждаемся, что таблицы есть

    for category, urls in categories.items():
        url1, url2, url3 = urls

        for product in Pars_All1(category, url1, find_all=0):
            price = product["Цена"].replace(" ", "")
            price = int(price) if price.isdigit() else price
            if category == "iPhone":
                process_iphone_product(product, category, "Магазин 1", conn)
            elif category == "Mac":
                process_mac_product(product, category, "Магазин 1", conn)
            else:
                save_product(conn, product["Модель"], category, "Магазин 1", product["Цена"],product["Наличие"] == "В наличии")

        for product in Pars_All2(category, url2, find_all=0):
            price = product["Цена"]
            price = int(price) if price.isdigit() else price
            if category == "iPhone":
                process_iphone_product(product, category, "Магазин 2", conn)
            elif category == "Mac":
                process_mac_product(product, category, "Магазин 2", conn)
            else:
                product["Модель"] = product["Модель"].replace(" +", "")
                save_product(conn, product["Модель"], category, "Магазин 2", product["Цена"],product["Наличие"] == "В наличии")

        for product in Pars_All3(url3):
            price = product["Цена"].replace(" ", "")
            price = int(price) if price.isdigit() else price
            if category == "iPhone":
                process_iphone_product(product, category, "Магазин 3", conn)
            elif category == "Mac":
                process_mac_product(product, category, "Магазин 3", conn)
            else:
                save_product(conn, product["Модель"], category, "Магазин 3", product["Цена"],product["Наличие"] == "В наличии")
    save_iphones_to_json(IPHONES)
    save_macbooks_to_json(MacBooks)


def cleanup_old_prices(conn):
    """Удаляет записи о ценах и наличии, которым более 12 месяцев"""
    cursor = conn.cursor()
    six_months_ago = datetime.now() - timedelta(days=360)

    cursor.execute("DELETE FROM prices WHERE date < ?", (six_months_ago,))
    cursor.execute("DELETE FROM availability WHERE date < ?", (six_months_ago,))

    conn.commit()
    print("Старые записи успешно удалены.")


def find_products_by_params(category: str, filters: dict, conn):
    cursor = conn.cursor()

    query = """
    SELECT p.id as product_id, p.model, p.store, pr.price
    FROM products p
    JOIN (
        SELECT product_id, MAX(date) as max_date
        FROM prices
        GROUP BY product_id
    ) latest ON latest.product_id = p.id
    JOIN prices pr ON pr.product_id = latest.product_id AND pr.date = latest.max_date
    WHERE p.category = ?
    """
    cursor.execute(query, (category,))
    results = cursor.fetchall()
    # conn.close()

    filtered = []
    for row in results:
        model_str = row[1].lower()  # Приводим к нижнему регистру для унификации
        match_all = True

        for value in filters.values():
            value = str(value).lower()
            if value not in model_str:
                match_all = False
                break

        if match_all:
            filtered.append(dict(zip([column[0] for column in cursor.description], row)))

    return filtered


def add_to_my_list(product_id: int, conn):
    cursor = conn.cursor()

    # Проверяем, есть ли уже товар в списке
    cursor.execute("SELECT 1 FROM my_list WHERE product_id = ?", (product_id,))
    if not cursor.fetchone():
        # Добавляем новый товар с Notice=0 по умолчанию
        cursor.execute("""
            INSERT INTO my_list (product_id, Notice)
            VALUES (?, 0)
        """, (product_id,))
        conn.commit()
    # conn.close()


async def get_my_list(conn):
    """Возвращает список товаров с последними ценами и статусом уведомлений"""
    cursor = conn.cursor()

    query = """
    SELECT 
        p.id, 
        p.model, 
        p.category, 
        p.store, 
        pr.price,
        pr.date as price_date,
        ml.Notice as notice_status
    FROM my_list ml
    JOIN products p ON ml.product_id = p.id
    JOIN (
        SELECT product_id, MAX(date) as max_date
        FROM prices
        GROUP BY product_id
    ) latest ON latest.product_id = p.id
    JOIN prices pr ON pr.product_id = latest.product_id AND pr.date = latest.max_date
    ORDER BY p.model
    """
    cursor.execute(query)
    results = cursor.fetchall()

    return [dict(zip([column[0] for column in cursor.description], row)) for row in results]

def is_in_my_list(product_id: int, conn) -> bool:
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM my_list WHERE product_id = ?", (product_id,))
    result = cursor.fetchone()
    # conn.close()
    return result is not None

def remove_from_my_list(product_id: int, conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM my_list WHERE product_id = ?", (product_id,))
    conn.commit()
    # conn.close()

def get_update_interval(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT update_interval_days FROM Settings WHERE id = 1")
    row = cursor.fetchone()
    return row[0] if row else 4


def set_update_interval(conn, days: int):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Settings (id, update_interval_days)
        VALUES (1, ?)
        ON CONFLICT(id) DO UPDATE SET update_interval_days = excluded.update_interval_days
    """, (days,))
    conn.commit()