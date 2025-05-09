from Exel.main_exel import export_to_excel
from Db.main_db import parse_and_save, cleanup_old_prices
import sqlite3


def main():
    conn = sqlite3.connect("Db/products.db")
    # Парсим данные и сохраняем в БД
    parse_and_save(conn)
    cleanup_old_prices(conn)
    # Экспортируем в Excel
   # export_to_excel(conn)
    # Закрываем соединение
    conn.close()
    print("Соединение с БД закрыто.")


if __name__ == '__main__':
    main()