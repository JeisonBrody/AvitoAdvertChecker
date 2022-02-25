import requests
from bs4 import BeautifulSoup
from config import url
import json
from bd import BD


def pars(id_client, City, Brand, pMin="0", pMax="10000000", Radiuss="0"):
    base = BD('bd_bot')

    with open("diction.json") as f:
        city = json.load(f)["city"]
    with open("diction.json") as f:
        brand = json.load(f)["brand"]

    payload = {
        "pmin": pMin,  # Цена от
        'pmax': pMax,  # Цена до
        'categoryId': '9',  # Категория машин на авито
        'params[110000]': brand[Brand],  # Марка авто
        'locationId': city[City],  # Город
        'radius': Radiuss,  # Радиус поиска
        's': "104"  # Сортировка объявлений по дате
    }
    proxies = {}

    # res = check_with_proxy(payload, proxies)  # Запрос с прокси
    res = check_without_proxy(payload)  # Запрос без прокси

    soup = BeautifulSoup(res.content, "lxml")
    last_advert_id = soup.find("div", attrs={"data-marker": "item"})["data-item-id"]  # id объявления Авто
    """Если ID объявления в бд != последнему спаршеному объявлению, то записываем в бд и возвращаем строку с инфой"""
    if base.get_info(id_client)[2] != int(last_advert_id):
        last_name = soup.find("h3", attrs={"itemprop": "name"}).text.replace(',', '') + " год, "  # Марка и год авто
        last_price = soup.find("meta", attrs={"itemprop": "price"})["content"] + " ₽, "  # Цена авто
        last_con = soup.find("div", attrs={"data-marker": "item-specific-params"}).text  # Параметры авто
        last_href = soup.find("a", attrs={"itemprop": "url"})["href"]
        info_auto = last_name + last_price + last_con + "\n" + "https://www.avito.ru/" + last_href
        base.update_id_advert(id_client, last_advert_id)  # Записываем ID объявление
        return "Кажется я нашел новое объявление!\n" + info_auto + "\n" + "Для завершения - /stop"  # Возвращаем id
        # объявления и информацию авто
    else:
        pass


def check_with_proxy(payload, proxies):  # запрос с прокси
    for http, proxy in proxies.items():
        print(http + proxy)
        res = requests.post(url, data=payload, proxies={http: proxy})
        if res.status_code == 200:
            print("Done:", res.status_code)
            return res
        else:
            print("Error:", res.status_code)
            continue
    print("PARSER DOWN, EXIT!")
    exit()


def check_without_proxy(payload):  # запрос без прокси
    res = requests.post(url, data=payload)
    if res.status_code == 200:
        print("Done:", res.status_code)
        return res
    else:
        print("Error:", res.status_code)
        print("PARSER DOWN, EXIT!")
        exit()


if __name__ == "__main__":
    pars()
