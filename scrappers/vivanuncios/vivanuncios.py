import os
import csv
import sys
import json

import requests
from bs4 import BeautifulSoup
from urllib.request import urlretrieve

from pprint import pprint as pp

BASE_URL = 'https://www.vivanuncios.com.mx'

# In this version I only scrape sell houses at CDMX
TEST_PATH = "/s-casas-en-venta/distrito-federal/v1c1293l1008p1"

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

count = 0
properties = []


def scrape(url, limit = 1):
    #ToDo: modularize this function

    global count
    global properties

    count += 1

    if(count > limit):
        print("Limit reached!")
        return

    response = requests.get(url)

    soup = BeautifulSoup(response.content, 'html.parser')

    properties_card = soup.find(
        "div", "viewport-contents").find_all("div", 'mapView')

    for property_card in properties_card:

        description = property_card.find(
            'div', 'expanded-description').get_text()

        data_set_image = property_card.find('picture').find(
            "source", type="image/jpeg").get('data-srcset')
        cover_image = data_set_image or property_card.find(
            'picture').find("img").get('src')

        raw_price = property_card.find("span", class_="ad-price").get_text()
        price = " ".join(raw_price.split())

        title_anchor = property_card.find(
            'div', 'tile-desc').find("a", class_="href-link")
        title = title_anchor.get_text().strip()
        link = title_anchor.get('href')

        uuid = link.split('/')[-1]

        properties.append({
            "uuid": uuid,
            "title": title,
            "price": price,
            "cover": cover_image,
            "link": BASE_URL + link,
            "description": description
        })

    # If you need attach more pages use mode="a" (append)...
    # with open('properties.json', mode="w") as f:
    with open(CURRENT_DIR + '/properties.json', mode="w") as f:
        f.write(json.dumps({"properties": properties}))

    print(f"{count} page done!")

    try:
        next_url = soup.find('div', id="pagination").find_all(
            'div', class_="desktop-pagination")[-1].find_all('a')[-1].get('href')

        scrape(BASE_URL + next_url)

    except:
        print("Unexpected error:", sys.exc_info()[0])


if __name__ == "__main__":
    scrape(BASE_URL + TEST_PATH)
