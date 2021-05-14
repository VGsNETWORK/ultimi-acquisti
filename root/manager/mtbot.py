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
    logger.info(_)
    logger.info(__)
    if message.chat:
        logger.info(f"checking {message.message_id}")
        return bool(purchase_exists(message.message_id, message.chat.id))


purchase_filter = filters.create(purchase_in_database)


class Mtbot:
    """Class to setup the bot with the Telegram Mtproto"""

    def __init__(self):
        logging.getLogger("pyrogram.syncer").setLevel(logging.WARNING)
        self.api_id = retrieve_key("API_ID")
        self.api_hash = retrieve_key("API_HASH")
        self.user = None
        self.app = None

    def setup_bot(self):
        """Setup the bot handlers"""
        logger.info("Configuring mtproto handlers")
        self.app.add_handler(
            MessageHandler(handle_purchase, filters=filters.regex("#ultimiacquisti"))
        )
        self.app.add_handler(
            MessageHandler(remove_purchase, filters=(filters.edited & purchase_filter))
        )

    def setup_userbot(self):
        """Setup the userbot handlers"""
        self.user.add_handler(DeletedMessagesHandler(deleted_purchase_message))

    def run_bot(self):
        """Run the bot"""
        self.app = Client("ultimiacquisti", api_id=self.api_id, api_hash=self.api_hash)
        self.setup_bot()
        self.app.run()

    def run_userbot(self):
        """run the userbot"""
        self.user = Client("userbot", api_id=self.api_id, api_hash=self.api_hash)
        self.setup_userbot()
        self.user.start()
