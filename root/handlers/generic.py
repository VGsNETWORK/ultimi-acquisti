#!/usr/bin/env python3

from root.model.rule import Rule
from bs4 import BeautifulSoup as bs4
from requests import Response
from html import unescape
from urllib.parse import unquote
import requests
import re


def de_html(data: str):
    if data:
        data: str = str(data)
        data: str = re.sub("<.*?>", "", data)
        data: str = re.sub(r"\n|(\s)?€(\s)?", "", unquote(unescape(data)))
        return re.sub(r"\t|\r", "", data)
    else:
        return None


def load_url(url: str) -> str:
    url = re.sub("http(s)?://", "", url)
    url = url.replace("//", "/")
    url = "https://%s" % url
    print("loading %s" % url)
    res: Response = requests.get(url)
    res.raise_for_status()
    return bs4(res.text, "lxml")


def extract_data(url: str, rules: dict) -> dict:
    data: bs4 = load_url(url)
    product: dict = {}
    for field in rules:
        rule = rules[field]
        if isinstance(rule, Rule):
            if rule.css:
                product[field] = de_html(data.find(rule.tag, rule.css))
            else:
                product[field] = de_html(data.find(rule.tag))
        else:
            product[field] = rule
    return data, product
