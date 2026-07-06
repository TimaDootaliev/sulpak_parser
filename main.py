import requests
from bs4 import BeautifulSoup, Tag
from bs4._typing import _SomeTags


BASE_URL = 'https://www.sulpak.kg/'

# https://www.sulpak.kg/f/smartfoniy?page=

"""
1. Получить html-код страницы
2. Из полученного html-кода отфильтровать данные:
   2.1 Получить все карточки с товарами
   2.2 Из каждой карточки вытянуть нужные данные 
3. Полученные привести в вид словаря
4. Сохранить данные в json/csv
"""

def get_html(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    # raise requests.HTTPError()
    return response.text

category_path = "f/smartfoniy"



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
            print('EMPTY CARD', card)
        else:
            data = {
                'name': name,
                'price': price,
                'description': description,
                'in_stock': in_stock,
                'reviews': reviews
            }
            result.append(data)
    return result


tag = 'div'
class_ = 'product__item-inner'
html = get_html(BASE_URL + category_path)
soup = get_soup(html)
cards = get_cards(soup, tag, class_)
parsed_data = parse_cards(cards)
print(parsed_data)
