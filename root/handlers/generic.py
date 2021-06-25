#!/usr/bin/env python3

import re


def de_html(data):
    data = str(data)
    return re.sub(r"<?.*>", "", data)