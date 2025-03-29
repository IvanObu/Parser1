import matplotlib.pyplot as plt
from datetime import datetime
def plot_price_history(conn, model, store):
    """Строит график изменения цены по товару"""
    cursor = conn.cursor()

    # Получаем ID товара
    cursor.execute("SELECT id FROM products WHERE model = ? AND store = ?", (model, store))
    result = cursor.fetchone()
    if not result:
        print("Товар не найден в базе данных.")
        return

    product_id = result[0]

    # Получаем историю цен
    cursor.execute("""
        SELECT date, price FROM prices 
        WHERE product_id = ? 
        ORDER BY date ASC
    """, (product_id,))
    rows = cursor.fetchall()

    if not rows:
        print("Нет истории цен для этого товара.")
        return

    dates = [datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") if isinstance(row[0], str) else row[0] for row in rows]
    prices = [row[1] for row in rows]

    # Строим график
    plt.figure(figsize=(10, 5))
    plt.plot(dates, prices, marker='o')
    plt.title(f"История цен: {model} ({store})")
    plt.xlabel("Дата")
    plt.ylabel("Цена")
    plt.grid(True)
    plt.tight_layout()
    plt.show()