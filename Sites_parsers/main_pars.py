headers = {"User-Agent": "CrookedHands/2.0 (EVM x8), CurlyFingers20/1;p"}
import requests
from bs4 import BeautifulSoup

def Pars_All1(category, url, find_all: int = 0):
    page = 1
    break_out_flag = False
    while True:
        category_url = f"{url}?PAGEN_1={page}"
        response = requests.get(category_url, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")  # or html.parser

        next_page = soup.find("a", class_="paging__next")
        if next_page and (break_out_flag == False):  # checking last page without "next"
            Cards = soup.find_all("div", class_="prod-card")
            page += 1

            for card in Cards:
                Avail_block = card.find("div", class_="prod-card__count icon-check-green nodesktop")
                if Avail_block:
                    Avail = Avail_block.text.strip()
                elif not find_all:
                    break_out_flag = True
                    break
                else:
                    Avail = "Нет в наличии"

                Description_block = card.find("div", class_="prod-card__title")
                Description = Description_block.text.strip() if Description_block else "Без названия"

                Price_block = card.find("div", class_="price__now")
                Price = (Price_block.contents[0].strip() if Price_block else "Без цены")

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

        if Cards and (break_out_flag == False) and (False if (category=="Ipad" and page == 2) else True ):  # checking last page without "next"
            if (category == "Mac" and page == 1):
                url = "https://ipiter.ru/shop/mac/1/page/"
            page += 1
            for card in Cards:
                Price_block = card.find("span", class_="price")
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
                Avail = "В наличии"
                yield {"Модель": Description, "Цена": Price, "Наличие": Avail}
        else:
            break
