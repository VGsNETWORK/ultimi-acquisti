#!/usr/bin/env python3

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class ExtractorHandler:
    base_url: str
    match: str
    load_picture: callable
    validate: callable
    extract_code: callable
    extract_data: callable
    extract_missing_data: callable
    get_extra_info: callable
    rule: Dict = field(default_factory=dict)