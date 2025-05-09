headers = {"User-Agent": "CrookedHands/2.0 (EVM x8), CurlyFingers20/1;p"}
import requests
from bs4 import BeautifulSoup
import re


COLOR_REPLACEMENTS_16_15_3 = {
    "пустынный титан": "Desert Titanium",
    "натуральный титан": "Natural Titanium",
    "белый титан": "White Titanium",
    "черный титан": "Black Titanium",
    "синий титан": "Blue Titanium",
    "ультрамарин": "Teal",
    "розовый": "Pink",
    "белый": "White",
    "бирюзовый": "Teal",
    "черный": "Black",
    "зелёный": "Teal",
    "зеленый": "Teal",
    "голубой": "Blue",
    "желтый": "Yellow",
    "темная ночь": "Black",
    "чёрный": "Black",
    "(серый)": "",

}

COLOR_REPLACEMENTS_16_15_2 = {
    "(Пустынный титан)": "",
    "(Пустынный Титан)": "",
    "(Природный титан)": "",
    "(Натуральный титан)": "",
    "(Белый титан)": "",
    "(Чёрный титан)": "",
    "(Синий титан)": "",
    "(Ультрамарин)": "",
    "(Розовый)": "",
    "(Белый)": "",
    "(Бирюзовый)": "",
    "(Черный)": "",
    "(черный)": "",
    "(Зелёный)": "",
    "(Синий)": "",
    "(Желтый)": "",
    "(Чёрный)": "",
    "(Бронзовый)": "",
    "(Серый)": "",
    "Ultramarine": "Teal",
    "без коробки и кабеля":"",
    "чёрный": "Black",
    "(серый)": "",
}

COLOR_REPLACEMENTS_16_15_1 = {
    "(Пустынный титан)": "",
    "(Натуральный титан)": "",
    "(синий)": "",
    "(Белый титан)": "",
    "(Черный титан)": "",
    "(Черный)": "",
    "(Синий титан)": "",
    "(Ультрамарин)": "",
    "(розовый)": "",
    "(белый)": "",
    "(бирюзовый)": "",
    "(черный)": "",
    "(чёрный)": "",
    "(зелёный)": "",
    "(зеленый)": "",
    "(White)": "",
    "(желтый)": "",
    "(бронзовый)": "",
    "(серый)": "",
    "черный": "",
    "чёрный": "",
    "зелёный": "Teal",
    "зеленый": "Teal",
    "Ultramarine": "Teal",
    "желтый": "Yellow",
    "голубой": "Teal",
    "розовый": "Pink",
    "(PRODUCT)RED": "Red",
}

COLOR_REPLACEMENTS_14_13_1 = {
    "красный": "Red",
    "синий": "Blue",
    "(Синий)": "",
    "(Тёмная ночь)": "",
    "(Зелёный)": "",
    "(Сияющая звезда)": "",
    "(Красный)": "",
    "чёрный": "Black",
    "черный": "Black",
    "желтый": "Yellow",
    "белый": "White",
    "зеленый": "Green",
    "розовый": "Pink",
    "фиолетовый": "Purple",
    "золотой": "Gold",
    "(Розовый)": "",
    "(PRODUCT)RED": "Red",
}

COLOR_REPLACEMENTS_14_13_2 = {
    "(Серебристый)": "",
    "Silver": "White",
    "(Тёмная ночь)": "",
    "Midnight": "Black",
    "тёмная ночь": "Black",
    "синий": "Blue",
    "(Синий)": "",
    "(Красный)": "",
    "(Фиолетовый)": "",
    "(Сияющая звезда)": "",
    "Starlight": "White",
    "(Серебристый)": "",
    "(Желтый)": "",
    "(Космический черный)": "",
    "Space Black": "",
    "Deep Purple": "",
    "(Золотистый)": "",
    "(PRODUCT)RED": "Red",
    "золотой": "Gold",
    "голубой": "Blue",
    "черный космос": "Black",
    "желтый": "Yellow",
    "сияющая звезда": "White",
    "фиолетовый": "Purple",
    "золотой": "Gold",
    "(Тёмная ночь)": "",
    "Midnight": "Black",
    "синий": "Blue",
    "(Зелёный)": "",
    "(Розовый)": "",
    "без коробки и кабеля":"",
    "черный": "Black",
}

COLOR_REPLACEMENTS_14_13_3 = {
    "(PRODUCT)RED": "Red",
    "голубой": "Blue",
    "черный космос": "Black",
    "желтый": "Yellow",
    "сияющая звезда": "White",
    "фиолетовый": "Purple",
    "золотой": "Gold",
    "(Тёмная ночь)": "",
    "Midnight": "Black",
    "темная ночь": "Black",
    "синий": "Blue",
    "черный": "Black",
}

COLOR_REPLACEMENTS_11_12_1_3 = {
    "(PRODUCT)RED": "Red",
    "(Белый)": "White",
    "(Черный)": "Black",
    "(Синий)": "Blue",
    "(Зеленый)": "Green",
    "(Фиолетовый)": "Purple",
    "белый": "White",
    "черный": "Black",
    "(Красный)": "",
}

COLOR_REPLACEMENTS_11_12_2 = {
    "(Красный)": "",
    "(Белый)": "",
    "(Чёрный)": "",
    "(Зелёный)": "",
    "(Фиолетовый)": "",
    "(Синий)": "",
    "без аксессуаров и коробки": "",
}

DATE_REPLACEMENTS_MAC_IPAD = {
    "дюймов": "",
    # "(2020)": "",
    # "(2021)": "",
    # "(2022)": "",
    # "(2023)": "",
    # "(2024)": "",
    # "(2025)": "",
    # "2020": "",
    # "2021": "",
    # "2022": "",
    # "2023": "",
    # "2024": "",
    # "2025": "",
    "SSD":"",
}

Mac_1_2_3 = {
    "Gold": "Starlight",
    "(небесно-голубой)": "",
    "(серебристый)": "",
    "Retina 4,5K": "",
    "(золотой)": "",
    "(сияющая звезда)": "",
    "(темная ночь)": "",
    "(золотистый)": "",
    "(серый космос)": "",
    "серый космос": "Space Gray",
    "серебристый": "Silver",
    "чёрный космос": "Midnight Black",
    "черный космос": "Midnight Black",
    "золотой": "Starlight",
    "сияющая звезда": "Starlight",
    "темная ночь":"Midnight Black",
    "золотистый": "Starlight",
    "небесно-голубой": "Silver",
    "полуночный черный": "Midnight Black",
    "полночный": "Midnight Black",
    "черная полночь": "Midnight Black",
    "розовый": "Pink",
    "зеленый": "Green",
    "голубой": "Silver",
    "синий": "Silver",
    "оранжевый": "Orange",
    "фиолетовый": "Purple",
    "серый": "Space Gray",
    "черный": "Black",
    "mini": "Mini",
    "Моноблок": "",
    "Nano-texture": "",
    "Numeric Keyboard": "",
    "SSD": "",
    "Ноутбук": "",
    "2020": "",
    "2021": "",
    "2022": "",
    "2023": "",
    "2024": "",
    "2025": "",
    "Уценка": "",
    "(MU963)": "",
    "желтый": "Yellow",
    "серебро": "Silver",
}

def remove_after_color(text):
    colors = [
        "Space Gray", "Silver", "Midnight Black", "Starlight", "Pink", "Green",
        "Orange", "Purple", "Blue", "Yellow", "Gray", "Black"
    ]
    color_pattern = r"(" + "|".join(re.escape(color) for color in colors) + r")\b.*"
    return re.sub(color_pattern, r"\1", text)

def replace_colors(text, replacements):
    import re
    # Заменяем цвета без учета регистра
    pattern = re.compile("|".join(re.escape(k) for k in replacements.keys()), flags=re.IGNORECASE)

    def replacement_func(m):
        original = m.group(0)
        for key in replacements.keys():
            if key.lower() == original.lower():
                return replacements[key]
        return original

    new_text = pattern.sub(replacement_func, text)

    # Убираем лишние + в конце, лишние пробелы
    new_text = re.sub(r'\s*\+\s*$', '', new_text)
    new_text = re.sub(r'\s+', ' ', new_text)  # заменяем все подряд идущие пробелы на один
    return new_text.strip()  # убираем пробелы по краям


def replace_words(text, replacements):

    pattern = re.compile(r"\b(" + "|".join(re.escape(k) for k in replacements.keys()) + r")\b", flags=re.IGNORECASE)

    def replacement_func(m):
        return replacements.get(m.group(0).lower(), "")

    # Применяем замену
    new_text = pattern.sub(replacement_func, text)

    # Убираем лишние знаки, пробелы и символы
    new_text = re.sub(r'[+″]+', '', new_text)
    new_text = re.sub(r'\s+', ' ', new_text)
    return new_text.strip()

def Pars_All1(category, url, find_all: int = 0):
    page = 1
    break_out_flag = False
    while True:
        category_url = f"{url}?PAGEN_2={page}"
        response = requests.get(category_url, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")  # or html.parser

        next_page = soup.find("a", class_="pagination__link blog-page-next")
        if next_page and (break_out_flag == False):  # checking last page without "next"
            Cards = soup.find_all("div", class_="prodcard")
            page += 1

            for card in Cards:
                Avail_block = card.find("div", class_="prodcard__status icon-check-green m-yes nodesktop")
                if Avail_block:
                    Avail = Avail_block.text.strip()
                elif not find_all:
                    break_out_flag = True
                    break
                else:
                    Avail = "Нет в наличии"

                Description_block = card.find("a", class_="prodcard__name")
                Description = Description_block.text.strip() if Description_block else "Без названия"
                if "Apple iPhone 16" in Description:
                    Description = replace_colors(Description, COLOR_REPLACEMENTS_16_15_1)
                elif "Apple iPhone 15" in Description:
                    Description = replace_colors(Description, COLOR_REPLACEMENTS_16_15_1).replace("1024GB", "1TB").replace("Teal", "Green")
                elif "Apple iPhone 14" in Description or "Apple iPhone 13" in Description or "SE" in Description:
                    Description = replace_colors(Description, COLOR_REPLACEMENTS_14_13_1).replace("1024GB", "1TB")
                elif "Apple iPhone 12" in Description or "Apple iPhone 11" in Description:
                    Description = replace_colors(Description, COLOR_REPLACEMENTS_11_12_1_3).replace("mini", "Mini")
                elif "Mac" in Description:
                    Description = replace_words(Description, Mac_1_2_3).replace('"', "").replace("(Silver)", "").replace("(Midnight Black)", "").replace("(Space Grey) ", "")
                    Description = remove_after_color(Description).replace("Гб", "GB").replace("Тб", "TB").replace("ГБ", "GB").replace("ТБ", "TB")
                elif "SE" not in Description:
                    Description = replace_words(Description, DATE_REPLACEMENTS_MAC_IPAD).replace('"', "").replace("1024GB", "1TB")
                Price_block = card.find("div", class_="prodcard__price")
                Price = (Price_block.contents[0].strip().replace("₽", '') if Price_block else "Без цены")
                yield {"Модель": Description, "Цена": Price, "Наличие": Avail}
        else:
            break

def Pars_All2(category, url, find_all: int = 0):
    page = 1
    break_out_flag = False
    while True:
        category_url = f"{url}{page}"
        response = requests.get(category_url, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")  # or html.parser

        Cards = soup.find_all("div", class_="externalWatchKolvo miniwrapper")

        if (Cards and (break_out_flag == False) and (False if (category=="Ipad" and page == 2) else True )):  # checking last page without "next"
            if (category == "Mac" and page == 1):
                url = "https://ipiter.ru/shop/mac/1/page/"
            page += 1
            for card in Cards:
                Price_block = card.find("span", class_="price")
                if "red" in str(Price_block):
                    Price = Price_block.find("span", class_="red").contents[0].strip()
                else:
                    Price = (Price_block.contents[0].strip().replace("₽", ''))
                if Price == "товар отсутствует":
                    if  not find_all:
                        break_out_flag = True
                        break
                    else:
                        Avail = str(Price) + str(Price_block.find("span").text)
                else:
                    if card.find("span", class_="price small"):
                        Avail = "Скоро в продаже"
                    else:
                        Avail = "В наличии"


                Description_block = card.find("h3", class_="product-name")
                Description = Description_block.text.strip() if Description_block else "Без названия"
                if "Apple iPhone 16" in Description:
                    Description = replace_colors(Description, COLOR_REPLACEMENTS_16_15_2)
                elif "Apple iPhone 15" in Description:
                    Description = replace_colors(Description, COLOR_REPLACEMENTS_16_15_2).replace("1024GB", "1TB").replace("Teal", "Green")
                elif "Apple iPhone 14" in Description or "Apple iPhone 13" in Description or "SE" in Description:
                    Description = replace_colors(Description, COLOR_REPLACEMENTS_14_13_2).replace("1024GB", "1TB")
                elif "Apple iPhone 12" in Description or "Apple iPhone 11" in Description:
                    Description = replace_colors(Description, COLOR_REPLACEMENTS_11_12_2)
                elif "Mac" in Description:
                    Description = replace_words(Description, Mac_1_2_3).replace('"', "").replace("/8/", " 8GB/").replace("/16/", " 16GB/").replace("/256 ", " 256GB ").replace("/512 ", " 512GB ")
                    Description = remove_after_color(Description).replace("Гб", "GB").replace("Тб", "TB")
                elif "SE" not in Description:
                    Description = replace_words(Description, DATE_REPLACEMENTS_MAC_IPAD).replace("+", "").replace("″", "")
                Description = Description.replace("()", "")
                yield {"Модель": Description, "Цена": Price, "Наличие": Avail}

        else:
            break



def Pars_All3(url):
    page = 1
    break_out_flag = False
    while True:
        category_url = f"{url}{page}"
        response = requests.get(category_url, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")  # or html.parser
        Cards = soup.find_all("div", class_="catalog-grid_item__xGxWb")
        page += 1
        if Cards and (break_out_flag == False):  # checking last page without "next"
            for card in Cards:
                Price_block = card.find("div", class_="price__now")
                Price = (Price_block.text.replace("\xa0", "").replace("₽", '') if Price_block else "Без цены")
                Description_block = card.find("div", class_="name_name__5zSxg name_wideOnMobile__yik1O")
                Description = Description_block.text.strip() if Description_block else "Без названия"
                if "Apple iPhone 16" in Description:
                    Description = replace_colors(Description, COLOR_REPLACEMENTS_16_15_3).replace("1024GB", "1TB")
                elif "Apple iPhone 15" in Description:
                    Description = replace_colors(Description, COLOR_REPLACEMENTS_16_15_3).replace("1024GB", "1TB").replace("Teal", "Green")
                elif "Apple iPhone 14" in Description or "Apple iPhone 13" in Description:
                    Description = replace_colors(Description, COLOR_REPLACEMENTS_14_13_3).replace("1024GB", "1TB")
                elif "Apple iPhone 12" in Description or "Apple iPhone 11" in Description:
                    Description = replace_colors(Description, COLOR_REPLACEMENTS_11_12_1_3)
                elif "Mac" in Description:
                    for color in Mac_1_2_3.keys():
                        color_pattern = re.compile(rf"\b{re.escape(color)}\b", flags=re.IGNORECASE)
                        match = color_pattern.search(Description)
                        if match:
                            color_found = match.group(0)
                            Description = color_pattern.sub("", Description).strip(", ")
                            Description = f"{Description}, {color_found}"
                            break
                    Description = replace_words(Description, Mac_1_2_3).replace('"', "").replace(".2", "").replace(".3","").replace(".6", "")
                    Description = remove_after_color(Description).replace("Гб", "GB").replace("Тб", "TB")
                elif "SE" not in Description:
                    Description = replace_words(Description, DATE_REPLACEMENTS_MAC_IPAD).replace("+", "").replace("″", "")
                Avail = "В наличии"
                yield {"Модель": Description, "Цена": Price, "Наличие": Avail}
        else:
            break

