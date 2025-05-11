import io
from datetime import datetime
import matplotlib.pyplot as plt
from typing import Tuple, Optional
import sqlite3


def generate_price_graph(conn: sqlite3.Connection, product_id: int) -> Tuple[Optional[io.BytesIO], str]:

    try:
        cursor = conn.cursor()

        cursor.execute("SELECT model, store FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()

        if not product:
            return None, "Товар не найден в базе данных"

        model, store = product

        # Получаем историю цен (только последнее значение за каждый день)
        cursor.execute("""
            WITH daily_prices AS (
                SELECT 
                    date(date) as day,
                    MAX(date) as last_time
                FROM prices
                WHERE product_id = ?
                GROUP BY day
            )
            SELECT p.date, p.price
            FROM prices p
            JOIN daily_prices dp ON p.date = dp.last_time
            WHERE p.product_id = ?
            ORDER BY p.date ASC
        """, (product_id, product_id))

        history = cursor.fetchall()

        if len(history) < 2:
            return None, "Недостаточно данных для построения графика"

        dates = []
        prices = []
        for row in history:
            date = row[0]
            if isinstance(date, str):
                try:
                    date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try:
                        date = datetime.strptime(date, "%Y-%m-%d")
                    except ValueError:
                        continue
            dates.append(date)
            prices.append(row[1])

        if len(dates) < 2:
            return None, "Недостаточно корректных данных"

        # Создаем график
        plt.figure(figsize=(10, 6), dpi=100)

        # Основной график
        plt.plot(dates, prices,
                 marker='o',
                 linestyle='-',
                 color='#4CAF50',
                 linewidth=2,
                 markersize=8,
                 markerfacecolor='#FF5722')

        plt.title(f"История цен: {model[:50] + '...' if len(model) > 50 else model}",
                  pad=20, fontsize=14)
        plt.xlabel("Дата", fontsize=12)
        plt.ylabel("Цена, руб", fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Аннотация последней цены
        last_price = prices[-1]
        plt.annotate(f'Текущая: {last_price} руб',
                     xy=(dates[-1], last_price),
                     xytext=(10, 10),
                     textcoords='offset points',
                     bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                     arrowprops=dict(arrowstyle='->'))

        # Сохраняем в буфер
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        buf.seek(0)
        plt.close()


        caption = (
            f"📊 История цен (последние значения за день)\n"
            f"📌 Товар: {model}\n"
            f"🛒 Магазин: {store}\n"
            f"🏷 Текущая цена: {last_price} руб\n"
            f"📅 Период: {dates[0].strftime('%d.%m.%Y')} - {dates[-1].strftime('%d.%m.%Y')}"
        )

        return buf, caption

    except Exception as e:
        return None, f"Ошибка при построении графика: {str(e)}"