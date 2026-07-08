import json
import csv

import requests
from bs4 import BeautifulSoup, Tag
from bs4._typing import _SomeTags
from tqdm import tqdm


"""
1. Получить html-код страницы
2. Из полученного html-кода отфильтровать данные:
   2.1 Получить все карточки с товарами
   2.2 Из каждой карточки вытянуть нужные данные 
3. Полученные привести в вид словаря
4. Сохранить данные в json/csv
"""


BASE_URL = 'https://www.sulpak.kg'

def get_html(url: str, page_number: int = 1) -> str:
    response = requests.get(url, params={'page': page_number})
    response.raise_for_status()
    # raise requests.HTTPError()
    return response.text


def get_soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, 'html.parser')


def get_cards(soup: BeautifulSoup, tag: str, class_: str) -> _SomeTags:
    cards = soup.find_all(tag, {'class': class_})
    return cards


def parse_cards(cards: _SomeTags) -> list[dict]:
    class_names = {
        "name": "product__item-name",
        "price": "product__item-price",
        "description": "product__item-description",
        "in_stock": "product__item-showcase",
        "reviews": "product__item-reviews"
    }

    def find_info(card: Tag, tag='div', attr=None) -> str:
        if attr:
            return card.find(tag, {'class': attr}).get_text(strip=True) # empty_card.text
        return card.find(tag).get_text(strip=True)

    result = []
    for card in cards:
        try:
            name = find_info(card, attr=class_names['name'])  # empty_card - Iphone
            price = find_info(card, attr=class_names['price'])
            description = find_info(card, attr=class_names['description'])
            in_stock = find_info(card, attr=class_names['in_stock'])
            reviews = find_info(card, attr=class_names['reviews'])
        except AttributeError:
            continue
        else:
            data = {
                'name': name,
                'price': int(price.replace('сом', '').replace(' ', '').strip()),
                'description': description,
                'in_stock': in_stock,
                'reviews': reviews
            }
            result.append(data)
    return result


def save_to_json(data: list[dict], filename: str) -> None:
    with open(f'data/{filename}.json', 'w') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def save_to_csv(data: list[dict], filename: str) -> None:
    with open(f'data/{filename}.csv', 'w') as file:
        fieldnames = ('name', 'price', 'description', 'in_stock', 'reviews')
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(data)


def parse_by_page(page_number, category):
    tag = 'div'
    class_ = 'product__item-inner'

    all_cards = []
    for page in range(1, page_number):  # (1, 2, 3, 4)
        html = get_html(BASE_URL + category, page)
        soup = get_soup(html)
        cards_from_one_page = get_cards(soup, tag, class_)
        all_cards.extend(cards_from_one_page)

    parsed_data = parse_cards(all_cards)
    return parsed_data


def get_categories(soup: BeautifulSoup) -> list[str]:
    tags_with_categories = soup.find_all('a', {'data-object': 'main_first_row_web'})
    links = []
    for tag in tqdm(tags_with_categories, desc='Парсим категории ...'):
        link = tag.get('href')
        if link.startswith('http'):
            continue
        links.append(link)

    return links


def parse_by_category(categories: list[str]) -> list[dict]:
    category_names = get_categories_names(categories)
    for category, category_name in zip(categories, category_names):
        parsed_data = parse_by_page(2, category)  # TODO: parse max page from sulpak and pass it to page number
        save_to_csv(parsed_data, category_name)
        save_to_json(parsed_data, category_name)


def get_categories_names(categories: list[str]) -> list[str]:
    return [category.split('/')[2] for category in categories]


html = get_html(BASE_URL)
soup = get_soup(html)
categories = get_categories(soup)
parse_by_category(categories)
