from Exel.main_exel import export_to_excel
from Db.main_db import parse_and_save, cleanup_old_prices
from Graphics.main_graphic import plot_price_history
import sqlite3


def main():
    # Открываем соединение с БД
    conn = sqlite3.connect("Db/products.db")

    # Парсим данные и сохраняем в БД

    parse_and_save(conn)
    cleanup_old_prices(conn)
    # Экспортируем в Excel
    export_to_excel(conn)
    plot_price_history(conn, model="Apple iPhone 15 Pro 128Gb  Natural Titanium (Природный титан) Nano-Sim + Nano-Sim", store="Магазин 2")
    # Закрываем соединение
    conn.close()
    print("Соединение с БД закрыто.")


if __name__ == '__main__':
    main()