from itertools import product

from openpyxl import Workbook
from Sicret import categories
from Sites_parsers.main_pars import Pars_All1, Pars_All2, Pars_All3


def main():
    wb = Workbook()
    first_sheet = True
    for category, urls in categories.items():  # Теперь urls — это кортеж из двух URL
        url1, url2, url3 = urls

        if first_sheet:
            ws = wb.active
            ws.title = category
            first_sheet = False
        else:
            ws = wb.create_sheet(title=category)

        # Заголовки таблицы
        ws.append(["Магазин", "Категория","Модель", "Цена", "Наличие"])

        for product in Pars_All1(category, url1, find_all=0):
            price = int(product["Цена"].replace(" ", ""))
            # Преобразуем цену в число, если это возможно
            try:
                price = int(price)
            except ValueError:
                pass
            ws.append(["Магазин 1", category ,product["Модель"], price, product["Наличие"]])

        for product in Pars_All2(category, url2, find_all=0):
            price = product["Цена"]

            try:
                price = int(price)
            except ValueError:
                pass
            ws.append(["Магазин 2", category ,product["Модель"], price, product["Наличие"]])

        for product in Pars_All3(url3):
            price = product["Цена"]

            # Преобразуем цену в число, если это возможно
            try:
                price = int(price)  # Или int(price), если цена всегда целая
            except ValueError:
                pass
            ws.append(["Магазин 3", category, product["Модель"], price, product["Наличие"]])

    excel_path = "apple_products.xlsx"
    wb.save(excel_path)
    print(f"Данные успешно сохранены в {excel_path}")