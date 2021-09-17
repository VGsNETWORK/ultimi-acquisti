#!/usr/bin/env python3

import re
from root.contants.constant import PLATFORMS_REGEX
from root.model.tracked_link import TrackedLink
from typing import List
from root.model.rule import Rule
from bs4 import BeautifulSoup as bs4
from root.model.extractor_handler import ExtractorHandler
from root.handlers.generic import extract_data
from root.util.util import de_html
import telegram_utils.utils.logger as logger
import requests
import json

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
    "bookable": False,
    "sold_out": False,
    "digital": False,
    "deals_end": None,
    "deals_percentage": 0.00,
}


def get_shipment_cost(price: float, string: bool = False):
    if price < 49:
        return "4,90" if string else 4.90
    else:
        return "" if string else 0.00


def is_valid_platform(platform: str):
    return re.search(PLATFORMS_REGEX, platform).group()


def is_bookable(data: bs4):
    path = data.find_all("script")[-6]
    if path:
        path = de_html(path).split("'")
        path = [line for line in path if "url" in line]
        if path:
            path = path[0].strip()
            path = re.sub('^.*url:|,.*|"', "", path)
            path = path.strip()
            headers = {"X-Requested-With": "XMLHttpRequest"}
            url = "https://%s%s" % (MATCH, path)
            print(url)
            data = requests.get(url, headers=headers)
            if data.status_code == 200:
                data = json.loads(data.content)
                return data["status"]["code"] == 6


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
    add_to_cart = data.find("a", {"id": "price-garancy"})
    product["bookable"] = is_bookable(data)
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
    platform = data.findAll("span", {"class": "label-categoria"})
    logger.info(platform)
    platform = [de_html(p) for p in platform]
    logger.info(platform)
    platform = next((p for p in platform if is_valid_platform(p)), None)
    if platform:
        logger.info("FOUND PLATFORM [%s]" % platform)
        product["platform"] = platform
    logger.info(product)
    return product


def get_extra_info(tracked_link: TrackedLink):
    delivery_available = "✅" if tracked_link.delivery_available else "❌"
    bookable = "✅" if tracked_link.bookable else "❌"
    if (
        tracked_link.collect_available
        or tracked_link.delivery_available
        or tracked_link.bookable
    ):
        available = "✅"
    else:
        available = "❌"
    if tracked_link.price < 49:
        extra_price = " a %s €" % get_shipment_cost(tracked_link.price, True)
    else:
        extra_price = " gratuita"
    if tracked_link.bookable:
        return "%s  Preordine\n%s  Spediz.%s\n\n" % (
            bookable,
            delivery_available,
            extra_price,
        )
    else:
        if tracked_link.price > 0:
            return "%s  Disponib.\n%s  Spediz.%s\n\n" % (
                available,
                delivery_available,
                extra_price,
            )
        else:
            return "❌  Preordine\n%s  Spediz.%s\n\n" % (
                bookable,
                delivery_available,
                extra_price,
            )


# fmt: off
multiplayer_handler: ExtractorHandler = \
    ExtractorHandler(BASE_URL, MATCH, load_picture, validate, \
        extract_code, extract_data, extract_missing_data, get_extra_info, get_shipment_cost, RULE)
# fmt: on