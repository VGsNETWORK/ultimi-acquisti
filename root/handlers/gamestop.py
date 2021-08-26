#!/usr/bin/env python3

from root.model.tracked_link import TrackedLink
from root.handlers.generic import extract_data
from root.model.rule import Rule
from bs4 import BeautifulSoup as bs4
from root.model.extractor_handler import ExtractorHandler
import telegram_utils.utils.logger as logger
import re
from typing import List

BASE_URL = "www.gamestop.it/"
MATCH = "gamestop.it"
RULE = {
    "title": Rule("div", {"class": "prodTitle"}),
    "price": Rule("span", {"class", "prodPriceCont"}),
    "platform": Rule("span", {"class": "platLogo"}),
    "store": "GameStop",
    "base_url": BASE_URL,
    "bookable": False,
    "delivery_available": False,
    "collect_available": False,
}


def get_shipment_cost(price: float, string: bool = False):
    if price < 40:
        return "5,00" if string else 5.00
    else:
        return "" if string else 0.00


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
    url = re.sub("https://|http://", "", url)
    code: List[str] = re.sub(r"(www.)?gamestop.it(/)?", "", url)
    logger.info("THIS IS THE CODE [%s]" % code)
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
    availability = data.find_all("img", {"class": "availabilityImg"})
    availability = availability[:2]
    for av in availability:
        src = av["src"]
        logger.info(src)
        if "Delivery" in str(av):
            product["delivery_available"] = "Available" in src
        else:
            product["collect_available"] = "Available" in src
    price = product["price"]
    if price:
        price = re.sub("€", "", price)
        price = re.sub(",", ".", price)
        product["price"] = float(price)
    else:
        product["price"] = 0
    product["platform"] = product["platform"].strip()
    bookable = data.find("p", {"content": "PreOrder"})
    product["bookable"] = True if bookable else False
    logger.info(product)
    return product


def get_extra_info(tracked_link: TrackedLink):
    collect_available = "✅" if tracked_link.collect_available else "❌"
    delivery_available = "✅" if tracked_link.delivery_available else "❌"
    bookable = "✅" if tracked_link.bookable else "❌"
    if tracked_link.bookable:
        return "%s  Prenotazione\n%s  Spedizione\n%s  Ritiro in negozio\n\n" % (
            bookable,
            delivery_available,
            collect_available,
        )
    else:
        if tracked_link.price > 0:
            return "%s  Spedizione\n%s  Ritiro in negozio\n\n" % (
                delivery_available,
                collect_available,
            )
        else:
            return "❌  Prenotazione\n%s  Spedizione\n%s  Ritiro in negozio\n\n" % (
                delivery_available,
                collect_available,
            )


# fmt: off
gamestop_handler: ExtractorHandler = \
    ExtractorHandler(BASE_URL, MATCH, load_picture, validate, \
        extract_code, extract_data, extract_missing_data, get_extra_info, get_shipment_cost, RULE)
# fmt: on