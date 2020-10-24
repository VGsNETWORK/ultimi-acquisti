#!/usr/bin/env python

import re
import logging
from root.util.logger import Logger
from pyrogram import Client, filters
from root.util.util import retrieve_key
from pyrogram.handlers import MessageHandler
from root.manager.purchase.handle_purchase import handle_purchase


class Mtbot:
    def __init__(self):
        logging.getLogger("pyrogram.syncer").setLevel(logging.WARNING)
        self.API_ID = retrieve_key("API_ID")
        self.API_HASH = retrieve_key("API_HASH")
        self.app = Client("ultimiacquisti", api_id=self.API_ID, api_hash=self.API_HASH)
        self.logger = Logger()

    def setup(self):
        self.app.add_handler(
            MessageHandler(handle_purchase, filters=filters.regex("#ultimiacquisti"))
        )

    def run(self):
        self.setup()
        self.app.run()
