#!/usr/bin/env python3

from bs4 import BeautifulSoup as bs4
from root.model.extractor_handler import ExtractorHandler


MATCH: str = "multiplayer.com"


def load_picture(data: bs4):
    pictures = data.find("div", {"id": "row-image-gallery"})
    pictures = pictures.findAll("a", {"data-gallery": "#gallery"})
    return [picture["href"] for picture in pictures]


def validate(data: bs4):
    data = data.find("div", {"class": "tout1_404_4Tell"})
    return False if data else True


multiplayer_handler: ExtractorHandler = ExtractorHandler(MATCH, load_picture, validate)