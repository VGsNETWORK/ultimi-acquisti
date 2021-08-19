#!/usr/bin/env python3

import re
from root.model.tracked_link import TrackedLink
from typing import List
from root.model.rule import Rule
from bs4 import BeautifulSoup as bs4
from root.model.extractor_handler import ExtractorHandler
from root.handlers.generic import extract_data
from root.util.util import de_html
import telegram_utils.utils.logger as logger

BASE_URL = "multiplayer.com/"
MATCH = "multiplayer.com"
RULE = {
    "title": Rule("h1", {"class": "titolo-prodotto"}),
    "price": "price",
    "platform": Rule("span", {"class": "label-categoria"}),
    "store": "Multiplayer",
    "base_url": BASE_URL,
    "delivery_available": True,
    "collect_available": False,
}


def load_picture(data: bs4):
    logger.info("loading pictures for multiplayer")
    pictures = data.find("div", {"id": "row-image-gallery"})
    if pictures:
        pictures = pictures.findAll("a", {"data-gallery": "#gallery"})
    else:
        pictures = data.findAll("a", {"class": "main-image"})
    return [picture["href"] for picture in pictures]


def validate(data: bs4):
    data = data.find("div", {"class": "tout1_404_4Tell"})
    return False if data else True


def extract_code(url: str) -> str:
    # https://multiplayer.com/videogiochi/playstation-4/nier-replicant-ver122474487139_453068.html
    url: str = re.sub("\?.*", "", url)
    url = re.sub("https://|http://", "", url)
    code: List[str] = re.sub(r"(www.)?multiplayer.com(/)?", "", url)
    if code:
        return code


def extract_missing_data(product: dict, data: bs4):
    price = data.findAll("script", {"type": "application/ld+json"})
    availability = data.find("div", {"class": "dyn-product-status"})
    product["delivery_available"] = True if availability else False
    if len(price) > 1:
        price: str = str(price[1])
        price: str = re.sub("<.*?>", "", price)
        price: str = next(
            (line for line in price.split("\n") if '"price"' in line), None
        )
        price: str = re.sub(r'.*:|"|,|\s', "", price)
        if price:
            product["price"] = float(price)
        else:
            product["price"] = 0
    logger.info(product)
    return product


def get_extra_info(tracked_link: TrackedLink):
    delivery_available = "✅" if tracked_link.delivery_available else "❌"
    return "%s  Disponibile\n\n" % (delivery_available)


# fmt: off
multiplayer_handler: ExtractorHandler = \
    ExtractorHandler(BASE_URL, MATCH, load_picture, validate, extract_code, extract_data, extract_missing_data, get_extra_info, RULE)
# fmt: on