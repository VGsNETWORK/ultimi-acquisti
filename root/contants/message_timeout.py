#!/usr/bin/env python3
from root.util.util import is_develop

"""Various timeouts for the messages"""

if is_develop():
    SERVICE_TIMEOUT = 10
    LONG_SERVICE_TIMEOUT = 3
    TWO_MINUTES = 12
    FIVE_MINUTES = 30
    ONE_MINUTE = 6
    THREE_MINUTES = 18
else:
    SERVICE_TIMEOUT = 10
    LONG_SERVICE_TIMEOUT = 30
    TWO_MINUTES = 120
    FIVE_MINUTES = 300
    ONE_MINUTE = 60
    THREE_MINUTES = 180
