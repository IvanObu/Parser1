from openpyxl import Workbook

def export_to_excel(conn):
    """Экспортирует данные из БД в Excel"""
    wb = Workbook()
    first_sheet = True
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT category FROM products")
    categories = [row[0] for row in cursor.fetchall()]

    for category in categories:
        if first_sheet:
            ws = wb.active
            ws.title = category
            first_sheet = False
        else:
            ws = wb.create_sheet(title=category)

        ws.append(["Магазин", "Категория", "Модель", "Последняя цена", "Наличие"])

        cursor.execute("""
            SELECT p.store, p.category, p.model, 
                   (SELECT price FROM prices WHERE product_id = p.id ORDER BY date DESC LIMIT 1) AS last_price,
                   (SELECT in_stock FROM availability WHERE product_id = p.id ORDER BY date DESC LIMIT 1) AS last_stock
            FROM products p
            WHERE p.category = ?
        """, (category,))

        for row in cursor.fetchall():
            ws.append(row)

    excel_path = "apple_products.xlsx"
    wb.save(excel_path)
    print(f"Данные успешно сохранены в {excel_path}")