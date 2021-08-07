#!/usr/bin/env python3

from dataclasses import dataclass


@dataclass
class ExtractorHandler:
    match: str
    load_picture: callable
    validate: callable
    extract_code: callable
    extract_data: callable
    extract_missing_data: callable