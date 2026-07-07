import json
import csv

import requests
from bs4 import BeautifulSoup, Tag
from bs4._typing import _SomeTags
from tqdm import tqdm


BASE_URL = 'https://www.sulpak.kg'

# https://www.sulpak.kg/f/smartfoniy?page=

"""
1. Получить html-код страницы
2. Из полученного html-кода отфильтровать данные:
   2.1 Получить все карточки с товарами
   2.2 Из каждой карточки вытянуть нужные данные 
3. Полученные привести в вид словаря
4. Сохранить данные в json/csv
"""

def get_html(url: str, page_number: int = 1) -> str:
    response = requests.get(url, params={'page': page_number})
    response.raise_for_status()
    # raise requests.HTTPError()
    return response.text


def get_soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, 'html.parser')



def get_cards(soup: BeautifulSoup, tag: str, class_: str) -> _SomeTags:
    cards = soup.find_all(tag, {'class': class_})
    return cards  # [<div>some info</div>, ]




# print(cards)

# phone = cards[0]
# print(phone.find('div', {'class': 'product__item-name'}).text)

class_names = {
    'name': 'product__item-name',
    'price': 'product__item-price',
    'description': 'product__item-description',
    'in_stock': 'product__item-showcase',
    # 'reviews_count' , tag - span
}

def parse_cards(cards: _SomeTags) -> list[dict]:
    def find_info(card: Tag, tag='div', attr=None) -> str:
        if attr:
            return card.find(tag, {'class': attr}).text # empty_card.text
        return card.find(tag).text

    result = []
    for card in cards:
        try:
            name = find_info(card, attr=class_names['name'])  # empty_card - Iphone
            price = find_info(card, attr=class_names['price'])
            description = find_info(card, attr=class_names['description'])
            in_stock = find_info(card, attr=class_names['in_stock'])
            reviews = find_info(card, 'span')
        except AttributeError:
            continue
        else:
            data = {
                'name': name.strip(),
                'price': int(price.replace('сом', '').replace(' ', '').strip()),
                'description': description.strip(),
                'in_stock': in_stock.strip(),
                'reviews': reviews.strip()
            }
            result.append(data)
    return result


def save_to_json(data: list[dict]) -> None:
    with open('data/data.json', 'w') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def save_to_csv(data: list[dict]) -> None:
    with open('data/data.csv', 'w') as file:
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
        cards_from_one_page = get_cards(soup, tag, class_) # [card1, card2]
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

# parsed_data = parse_by_page(2, 'f/piylesosiy')  # TODO: fix first page (page=1)

# print(len(parsed_data))

# save_to_json(parsed_data)
# save_to_csv(parsed_data)


def parse_by_category(categories: list[str]) -> list[dict]:
    all_results = []
    for category in categories:
        parsed_data = parse_by_page(2, category)
        all_results.extend(parsed_data)

    return all_results


html = get_html(BASE_URL)
soup = get_soup(html)
categories = get_categories(soup)

parsed_data = parse_by_category(categories)
save_to_json(parsed_data)
save_to_csv(parsed_data)
