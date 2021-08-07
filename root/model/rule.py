#!/usr/bin/env python3

from dataclasses import dataclass


@dataclass
class Rule:
    tag: str
    css: dict
