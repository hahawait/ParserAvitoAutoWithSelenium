# Авито. Парсинг автомобилей в Волгоградской области, город Волжский, радиус поиска 50км

import pandas
import time
import re

from pandas import ExcelWriter
from selenium import webdriver
from bs4 import BeautifulSoup

url = "https://www.avito.ru/volgogradskaya_oblast_volzhskiy/avtomobili?cd=1&radius=50&p=1"

def get_html(url):
    driver = webdriver.Chrome()
    driver.maximize_window()

    time.sleep(1)
    driver.get(url)
    time.sleep(1)
    html = driver.page_source

    driver.quit()
    return html

# Количество страниц
def get_pages(html):
    soup = BeautifulSoup(html, 'lxml')

    # Находим кол-во страниц, иначе количество страниц равно 1
    try:
        pages = soup.find('span', {'data-marker': 'pagination-button/next'}).previous_element
    except:
        pages = 1
    print('Количество найденных страниц: ', pages)
    return pages

def get_content(html, url):
    soup = BeautifulSoup(html, 'lxml')
    blocks = soup.find_all('div', class_=re.compile('iva-item-content'))
    data = []
    for block in blocks:
        data.append({
            "Наименование": block.find('h3', class_=re.compile('title-root')).get_text(strip=True),
            'Цена': block.find('span', class_=re.compile('price-text')).get_text(strip=True).replace('₽', '').replace(
                '\xa0', ''),
            'Город': block.find('a', class_=re.compile('link-link')).get('href').split('/')[1],
            'Район': block.find('div', class_=re.compile('geo-root')).get_text(strip=True),
            'Ссылка': url + block.find('a', class_=re.compile('link-link')).get('href'),
        })
    return data

def save_excel(data, file_name):
    # сохраняем полученные данные в эксель через pandas
    df_data = pandas.DataFrame(data)

    writer = ExcelWriter(f'{file_name}.xlsx')
    df_data.to_excel(writer, f'{file_name}')
    writer.save()
    print(f'Данные сохранены в файл "{file_name}.xlsx"')

def parse(url):
    html = get_html(url)
    pages = get_pages(html)
    data = []
    for page in range(1, int(input('Сколько страниц спарсить?\n'))+1):
        url = 'https://www.avito.ru/volgogradskaya_oblast_volzhskiy/avtomobili?cd=1&radius=50&p=' + str(page)
        html = get_html(url)
        data.extend(get_content(html, url))
    save_excel(data, 'Results')

parse(url)
