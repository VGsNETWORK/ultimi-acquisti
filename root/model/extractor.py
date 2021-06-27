#!/usr/bin/env python3

from dataclasses import dataclass
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
                return next(
                    (
                        handler.match in url
                        for handler in self.handlers
                        if handler.match in url
                    ),
                    False,
                )
            return False
        return False

    def validate_url(self, url):
        if not url:
            return False
        logger.info(re.findall("/\w+/?", url))
        url = re.sub("^.*//:", "", url)
        if not re.findall("/\w+/?", url):
            return False
        if not url.startswith("http"):
            url = "https://%s" % url
        data = requests.get(url)
        handler: ExtractorHandler = next(
            (handler for handler in self.handlers if handler.match in url), None
        )
        if handler:
            try:
                data.raise_for_status()
                data = bs4(data.content, "lxml")
                return handler.validate(data)
            except Exception:
                return False
        return False

    def load_url(self, url: str):
        if not url:
            return []
        if not url.startswith("http"):
            url = "https://%s" % url
        handler: ExtractorHandler = next(
            (handler for handler in self.handlers if handler.match in url), None
        )
        if handler:
            try:
                data = requests.get(url)
                data = bs4(data.content, "lxml")
                return handler.load_picture(data)
            except Exception as e:
                logger.warn("Unable to scrape %s cause: %s" % (url, e))
                return []
        else:
            return []
