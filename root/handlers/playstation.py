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
import requests
import json

BASE_URL = "store.playstation.com/it-it/"
MATCH = "store.playstation.com"
RULE = {
    "title": Rule("h1", {"class": "psw-t-title-l"}),
    "price": Rule("span", {"class": "psw-t-title-m"}),
    "platform": "Playstation",
    "store": "Playstation Store",
    "base_url": BASE_URL,
    "delivery_available": False,
    "collect_available": False,
    "bookable": False,
    "sold_out": False,
    "digital": True,
}


def get_shipment_cost(price: float, string: bool = False):
    return "" if string else 0.00


def is_bookable(data: bs4):
    bookable = data.find(
        "span", {"class": "psw-fill-x psw-t-truncate-1 psw-l-space-x-2"}
    )
    logger.info(bookable)
    bookable = de_html(bookable)
    return "pre-ordine" in str(bookable).lower()


def load_picture(data: bs4):
    script = data.find_all("script")[-21]
    script = de_html(script)
    try:
        script = json.loads(script)
        script = script["props"]["pageProps"]
        script = script["batarangs"]["background-image"]
        script = script["text"]
        script = de_html(script)
        script = json.loads(script)
        script = script["cache"]
        for key in script.keys():
            if "Concept" in key:
                continue
        media = script[key]["media"]
        media = [m["url"] for m in media if m["type"] == "IMAGE"]
        return media[:10]
    except KeyError:
        return []


def validate(data: bs4):
    logger.info("VALIDATING PLAYSTATION LINK")
    return data.find("span", {"class": "psw-t-title-m"}) != None


def extract_code(url: str) -> str:
    find_re = r"/concept/.*" if "/concept/" in url else r"/product/.*"
    code: List[str] = re.findall(find_re, url)
    if code:
        code: str = code[0]
        if code.startswith("/"):
            return code[1:]
        else:
            return code


def extract_platform(data: bs4):
    platform = data.find("div", {"class": "psw-l-space-x-2 psw-l-line-left psw-m-t-4"})
    logger.info(platform)
    platform = platform.find_all("span", {"class": "psw-p-x-2 psw-p-y-1 psw-t-tag"})
    logger.info(platform)
    platform = [de_html(p) for p in platform]
    logger.info(platform)
    platform = [p for p in platform if not "edition" in p.lower()]
    logger.info(platform)
    return ", ".join(platform)


def extract_missing_data(product: dict, data: bs4):
    product["platform"] = extract_platform(data)
    product["bookable"] = is_bookable(data)
    return product


def get_extra_info(tracked_link: TrackedLink):
    bookable = "✅" if tracked_link.bookable else "❌"
    if tracked_link.bookable:
        return "%s  Preordine" % bookable
    else:
        return "✅  Disponib."


# fmt: off
playstation_handler: ExtractorHandler = \
    ExtractorHandler(BASE_URL, MATCH, load_picture, validate, \
        extract_code, extract_data, extract_missing_data, get_extra_info, get_shipment_cost, RULE)
# fmt: on