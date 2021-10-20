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

BASE_URL = "multiplayer.com/shop/"
MATCH = "multiplayer.com"
RULE = {
    "title": Rule("h1", {"class": "te_product_name"}),
    "price": "price",
    "platform": "MISSING",
    "store": "Multiplayer",
    "base_url": BASE_URL,
    "delivery_available": True,
    "collect_available": False,
    "bookable": False,
    "sold_out": False,
    "digital": False,
    "deals_end": None,
    "deals_percentage": 0.00,
    "included_in_premium": False,
    "premium_type": "",
}


def get_shipment_cost(price: float, string: bool = False):
    if price < 49:
        return "4,90" if string else 4.90
    else:
        return "" if string else 0.00


def is_valid_platform(platform: str):
    logger.info(platform)
    return re.search(PLATFORMS_REGEX, platform).group()


def is_bookable(data: bs4):
    data = data.find("small", "text-primary")
    if data:
        return not "mt-2" in str(data)
    return False


def load_picture(data: bs4):
    try:
        images = data.find("script", {"type": "application/ld+json"})
        images = re.sub("<.*?>|\n\n", "", str(images))
        images = json.loads(images)
        return images["image"]
    except Exception as e:
        logger.error("unable to extract pictures")
        logger.error(e)
        return []


def validate(data: bs4):
    data = data.find_all("link")
    logger.info(data)
    return next((False for e in data if "404" in str(e)), True)


def extract_code(url: str) -> str:
    # https://multiplayer.com/videogiochi/playstation-4/nier-replicant-ver122474487139_453068.html
    url: str = re.sub("\?.*", "", url)
    url = re.sub(r"https://|http://", "", url)
    code: str = re.sub(r"^.*/shop/", "", url)
    if code:
        return code


def extract_missing_data(product: dict, data: bs4):
    # se disponibile
    availability = data.find("button", {"class": "submit-notify"})
    logger.info("IS AVAILABLE: %s" % availability)
    product["delivery_available"] = True if not availability else False
    # se prenotabile
    product["bookable"] = is_bookable(data)
    # prezzo
    price = data.find("span", {"class": "oe_currency_value"})
    if price:
        price: str = re.sub("<.*?>", "", str(price))
        if price:
            price: str = re.sub(",", ".", price)
            product["price"] = float(price)
        else:
            product["price"] = 0
    # piattaforma
    platform = data.find("li", {"data-attribute_name": "Piattaforma"})
    if platform:
        platform = platform.find("span")
        logger.info("PIATTAFORMA [%s]" % platform)
        logger.info("PIATTAFORMA [%s]" % de_html(platform))
        if platform:
            platform = de_html(platform)
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
            if tracked_link.delivery_available:
                return "%s  Disponib.\n%s  Spediz.%s\n\n" % (
                    available,
                    delivery_available,
                    extra_price,
                )
            else:
                return "%s  Disponib.\n\n" % (available)
        else:
            return "❌  Preordine\n\n" % (bookable)


# fmt: off
multiplayer_handler: ExtractorHandler = \
    ExtractorHandler(BASE_URL, MATCH, load_picture, validate, \
        extract_code, extract_data, extract_missing_data, get_extra_info, get_shipment_cost, RULE)
# fmt: on