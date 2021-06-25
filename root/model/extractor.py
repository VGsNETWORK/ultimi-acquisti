#!/usr/bin/env python3

from dataclasses import dataclass
from typing import List
from root.model.extractor_handler import ExtractorHandler
import requests
from bs4 import BeautifulSoup as bs4
import telegram_utils.utils.logger as logger


@dataclass
class Extractor:
    handlers: List[ExtractorHandler]

    def add_handler(self, handler: ExtractorHandler):
        self.handlers.append(handler)

    def is_supported(self, url: str):
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
                data.raise_for_status()
                data = bs4(data.content, "lxml")
                return handler.load_picture(data)
            except Exception as e:
                logger.warn("Unable to scrape %s cause: %s" % (url, e))
                return []
        else:
            return []
