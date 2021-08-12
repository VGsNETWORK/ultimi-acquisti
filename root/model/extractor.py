#!/usr/bin/env python3

from dataclasses import dataclass
from root.helper.subscriber_helper import update_subscriber
from root.helper.tracked_link_helper import (
    add_subscriber_to_link,
    find_link_by_code,
    update_or_create_scraped_link,
)
from root.model.tracked_link import TrackedLink
from typing import List
from root.model.extractor_handler import ExtractorHandler
import requests
from bs4 import BeautifulSoup as bs4
import telegram_utils.utils.logger as logger
import re


@dataclass
class Extractor:
    handlers: List[ExtractorHandler]

    def add_handler(self, handler: ExtractorHandler):
        self.handlers.append(handler)

    def is_supported(self, url: str):
        if self.validate_url(url):
            if url:
                return self.extractor_exists(url)
            return False
        return False

    def extract_code(self, url: str):
        handler: ExtractorHandler = next(
            (handler for handler in self.handlers if handler.match in url), None
        )
        if handler:
            return handler.extract_code(url)
        return None

    def format_price(self, price: str):
        price = str(price)
        price = re.sub(",", ".", price)
        return price

    def extractor_exists(self, url: str):
        return next(
            (handler.match in url for handler in self.handlers if handler.match in url),
            False,
        )

    def domain_duplicated(self, url: str, links: List[str]):
        domain = re.sub(r"^.*//:|www.|\..*", "", url)
        domains = [re.sub(r"^.*//:|www.|\..*", "", link) for link in links]
        return domain in domains

    def validate_url(self, url):
        if not url:
            return False
        logger.info(re.findall(r"/\w+/?", url))
        url = re.sub(r"^.*//:", "", url)
        if not re.findall(r"/\w+/?", url):
            return False
        if not url.startswith("http"):
            url = "https://%s" % url
        handler: ExtractorHandler = next(
            (handler for handler in self.handlers if handler.match in url), None
        )
        if handler:
            data = requests.get(url)
            try:
                data.raise_for_status()
                data = bs4(data.content, "lxml")
                return handler.validate(data)
            except Exception as e:
                logger.error(e)
                return False
        return False

    def load_url(self, url: str):
        if not url:
            return []
        if not url.startswith("http"):
            url = "https://%s" % url
            logger.info(url)
        handler: ExtractorHandler = next(
            (handler for handler in self.handlers if handler.match in url), None
        )
        if handler:
            logger.info("using handler [%s]" % handler.load_picture)
            try:
                logger.info("loading URL")
                data = requests.get(url)
                logger.info("extracting the data")
                data = bs4(data.content, "lxml")
                logger.info("extracting the photos")
                return handler.load_picture(data)
            except Exception as e:
                logger.warn("Unable to scrape %s cause: %s" % (url, e))
                return []
        else:
            return []

    def add_subscriber(self, link: str, user_id: int, product: dict):
        product["link"] = link
        update_or_create_scraped_link(product)
        tlink: TrackedLink = find_link_by_code(product["code"])
        if not user_id in tlink.subscribers:
            add_subscriber_to_link(product["code"], user_id)
            update_subscriber(user_id, product["code"], product["price"])

    def parse_url(self, url: str):
        if not self.is_supported(url):
            raise ValueError("No valid handler registered for the specfied url")
        # search for an valid handler for the url
        handler = next(
            (handler for handler in self.handlers if re.findall(handler.match, url)),
            None,
        )
        if handler:
            # extract the code with the handler
            code: str = handler.extract_code(url)
            if code.startswith("/"):
                code = code[1:]
            logger.info(url)
            url: str = "%s/%s" % (handler.base_url, code)
            logger.info(url)
            data, product = handler.extract_data(url, handler.rule)
            handler.extract_missing_data(product, data)
            product["code"] = code
            product["price"] = self.format_price(product["price"])
            return product
        else:
            # if no handler has been found, raise an error
            raise ValueError("No valid handler registered for the specfied url")
