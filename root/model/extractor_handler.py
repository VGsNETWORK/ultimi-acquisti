#!/usr/bin/env python3

from dataclasses import dataclass


@dataclass
class ExtractorHandler:
    match: str
    load_picture: callable
