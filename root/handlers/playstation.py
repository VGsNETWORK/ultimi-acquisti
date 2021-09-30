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
from datetime import datetime, time
from dateutil import tz, parser
from dateutil.relativedelta import relativedelta

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
    "deals_percentage": 0,
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
    try:
        platform = data.find(
            "div", {"class": "psw-l-space-x-2 psw-l-line-left psw-m-t-4"}
        )
        logger.info(platform)
        platform = platform.find_all("span", {"class": "psw-p-x-2 psw-p-y-1 psw-t-tag"})
        logger.info(platform)
        platform = [de_html(p) for p in platform]
        logger.info(platform)
        platform = [p for p in platform if not "edition" in p.lower()]
        logger.info(platform)
    except Exception:
        platform = ["PS4", "PS5"]
    return ", ".join(platform)


def has_date(date: str):
    return re.search(r"\d{1,2}/\d{1,2}/\d{4}\s\d{1,2}:\d{1,2}", date)


def has_percentage(content: str):
    return re.search(r"\d{1,3}%", content)


def deals_perc(data: bs4):
    try:
        data = data.find("div", {"class": "psw-c-bg-card-1"})
        deals_perc = data.find_all("span", {"class": "psw-m-r-3"})
        logger.info(deals_perc)
        if deals_perc:
            deals_perc = [de_html(n) for n in deals_perc]
            deals_perc = (next(n for n in deals_perc if has_percentage(n)), None)
            if deals_perc:
                deals_perc = de_html(deals_perc)
                deals_perc = re.search(r"\d{1,3}%", deals_perc)
                if deals_perc:
                    deals_perc = deals_perc[0]
                    deals_perc = float(deals_perc.replace("%", ""))
                    return deals_perc
    except Exception as e:
        logger.error(e)
    return 0.00


def deals_end(data: bs4):
    try:
        data = data.find("div", {"class": "psw-c-bg-card-1"})
        ending_date = data.find_all("span", {"class": "psw-c-t-2"})
        logger.info(ending_date)
        if ending_date:
            ending_date = [de_html(n) for n in ending_date]
            ending_date = (next(n for n in ending_date if has_date(n)), None)
            if ending_date:
                ending_date = de_html(ending_date)
                ending_date = re.search(
                    r"\d{1,2}/\d{1,2}/\d{4}\s\d{1,2}:\d{1,2}", ending_date
                )
                if ending_date:
                    ending_date = ending_date.group()
                    ending_date = datetime.strptime(ending_date, "%d/%m/%Y %H:%M")
                    return ending_date + relativedelta(hours=14)
    except Exception as e:
        logger.info(e)
    return None


def extract_missing_data(product: dict, data: bs4):
    product["platform"] = extract_platform(data)
    product["bookable"] = is_bookable(data)
    product["deals_end"] = deals_end(data)
    product["deals_percentage"] = deals_perc(data)
    logger.info(product)
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