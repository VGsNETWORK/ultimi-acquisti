#!/usr/bin/env python

""" File to manage the bot using the Telegram Mtproto library """

import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.handlers import MessageHandler, DeletedMessagesHandler
from pyrogram.filters import create
from root.manager.purchase.handle_purchase import handle_purchase
from root.manager.purchase.delete import deleted_purchase_message
from root.manager.purchase.delete import remove_purchase
import root.util.logger as logger
from root.util.util import retrieve_key
from root.helper.purchase_helper import purchase_exists


def purchase_in_database(_, __, message: Message) -> bool:
    """custom handler to check if a message is in the database

    Args:
        message (Message): The message recevied

    Returns:
        bool: If the message was a purchase
    """
    return bool(purchase_exists(message.message_id))


purchase_filter = filters.create(purchase_in_database)


class Mtbot:
    """Class to setup the bot with the Telegram Mtproto"""

    def __init__(self):
        logging.getLogger("pyrogram.syncer").setLevel(logging.WARNING)
        self.api_id = retrieve_key("API_ID")
        self.api_hash = retrieve_key("API_HASH")
        self.app = Client("ultimiacquisti", api_id=self.api_id, api_hash=self.api_hash)
        self.user = Client("userbot", api_id=self.api_id, api_hash=self.api_hash)

    def setup(self):
        """Setup the bot handlers"""
        logger.info("Configuring mtproto handlers")
        self.app.add_handler(
            MessageHandler(handle_purchase, filters=filters.regex("#ultimiacquisti"))
        )
        self.app.add_handler(
            MessageHandler(remove_purchase, filters=(filters.edited & purchase_filter))
        )
        self.user.add_handler(
            DeletedMessagesHandler(deleted_purchase_message, filters=purchase_filter)
        )

    def run(self):
        """Run the bot"""
        logger.info("running mtproto part of the bot")
        self.setup()
        self.app.start()
        self.user.run()
