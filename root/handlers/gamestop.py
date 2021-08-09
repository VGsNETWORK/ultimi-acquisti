#!/usr/bin/env python3

from root.handlers.generic import extract_data
from root.model.rule import Rule
from bs4 import BeautifulSoup as bs4
from root.model.extractor_handler import ExtractorHandler
import telegram_utils.utils.logger as logger
import re
from typing import List

BASE_URL = "https://www.gamestop.it/"
MATCH = "gamestop.it"
RULE = {
    "title": Rule("div", {"class": "prodTitle"}),
    "price": Rule("span", {"class", "prodPriceCont"}),
    "platform": Rule("span", {"class": "platLogo"}),
    "store": "GameStop",
    "base_url": BASE_URL,
}


def load_picture(data: bs4):
    pictures = data.find("div", {"class": "mainInfo"})
    main_picture = pictures.find("a", {"class": "prodImg"})
    pictures = pictures.findAll("a", {"class": "anc"})
    pictures = [picture["href"] for picture in pictures]
    pictures.insert(0, main_picture["href"])
    return pictures


def extract_code(url: str) -> str:
    # https://www.gamestop.it/Switch/Games/103268/mario-kart-8-deluxe
    url: str = re.sub("\?.*", "", url)
    code: List[str] = re.sub(r"https://www.gamestop.it/", "", url)
    if code:
        return code


def validate(data: bs4):
    data = data.find("fieldset", {"class": "err404"})
    logger.info(data)
    return False if data else True


def extract_missing_data(product: dict, data: bs4):
    title = product["title"]
    title = title.strip()
    title = title.strip().split("\n")[0]
    title = re.sub(r"\r|\n|\s\s", "", title)
    product["title"] = title

    price = product["price"]
    if price:
        price = re.sub("€", "", price)
        price = re.sub(",", ".", price)
        product["price"] = float(price)
    else:
        product["price"] = 0

    product["platform"] = product["platform"].strip()
    return product


# fmt: off
gamestop_handler: ExtractorHandler = \
    ExtractorHandler(BASE_URL, MATCH, load_picture, validate, extract_code, extract_data, extract_missing_data, RULE)
# fmt: on