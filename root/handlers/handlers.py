#!/usr/bin/env python3

from root.model.extractor import Extractor
from root.handlers.multiplayer import multiplayer_handler
from root.handlers.gamestop import gamestop_handler
from root.handlers.playstation import playstation_handler

extractor: Extractor = Extractor([])

extractor.add_handler(multiplayer_handler)
extractor.add_handler(gamestop_handler)
extractor.add_handler(playstation_handler)