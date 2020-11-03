#!/usr/bin/env python

""" File to manage the bot using the Telegram Mtproto library """

import logging
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from root.manager.purchase.handle_purchase import handle_purchase
import root.util.logger as logger
from root.util.util import retrieve_key


class Mtbot:
    """Class to setup the bot with the Telegram Mtproto"""

    def __init__(self):
        logging.getLogger("pyrogram.syncer").setLevel(logging.WARNING)
        self.api_id = retrieve_key("API_ID")
        self.api_hash = retrieve_key("API_HASH")
        self.app = Client("ultimiacquisti", api_id=self.api_id, api_hash=self.api_hash)

    def setup(self):
        """Setup the bot handlers"""
        logger.info("Configuring mtproto handlers")
        self.app.add_handler(
            MessageHandler(handle_purchase, filters=filters.regex("#ultimiacquisti"))
        )

    def run(self):
        """Run the bot"""
        logger.info("running mtproto part of the bot")
        self.setup()
        self.app.run()
