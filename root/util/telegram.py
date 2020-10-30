#!/usr/bin/env python3

""" This File contains a class with various telegram tools """

import threading
from time import sleep
from telegram import Bot, Message
from telegram.ext import CallbackContext
from telegram.error import Unauthorized, BadRequest
from root.util.logger import Logger
from root.util.util import retrieve_key


class TelegramSender:
    """ This class contains a class with various telegram tools """

    def __init__(self):
        self._logger = Logger()
        self._token = None
        self._bot = None

    def _bot_init(self, token: str):
        """initialize the bot to be used

        Args:
            token (str): Telegram token of the bot
        """
        if token == self._token:
            return
        self._bot = Bot(token)
        self._token = token

    def send_to_log(self, message: str):
        """Send a message to the log channel

        Args:
            message (str): The message to send
        """
        token = retrieve_key("TOKEN")
        log_channel = retrieve_key("ERROR_CHANNEL")
        self.send_message(token, log_channel, message)

    def send_message(self, token: str, chat_id: int, message: str, **kwargs):
        """send a message to a designed chat

        Args:
            token (str): Telegram token of the bot
            chat_id (int): The chat where to send the message
            message (str): The message to send
        """
        self._bot_init(token)
        try:
            self._logger.info("sending message to chat {}".format(chat_id))
            self._bot.send_message(chat_id=chat_id, text=message, **kwargs)
        except Unauthorized:
            self._logger.error("403 Unauthorized, bot token is wrong")
        except BadRequest:
            self._logger.error("400 Bad Request")

    def send_photo(
        self, token: str, chat_id: int, photo: bytes, caption: str, **kwargs
    ):
        """send a message to a designed chat

        Args:
            token (str): Telegram token of the bot
            chat_id (int): The chat where to send the message
            photo (bytes): The photo to send
            caption (str): The caption of the photo
        """
        self._bot_init(token)
        try:
            self._logger.info("sending photo to chat {}".format(chat_id))
            self._bot.send_photo(
                chat_id=chat_id, photo=photo, caption=caption, **kwargs
            )
        except Unauthorized:
            self._logger.error("403 Unauthorized, bot token is wrong")
        except BadRequest:
            self._logger.error("400 Bad Request")

    def send_and_delete(
        self,
        context: CallbackContext,
        chat_id: int,
        text: str,
        reply_markup=None,
        reply_to_message_id: int = None,
        parse_mode: str = "HTML",
        timeout: int = 360,
    ):
        """Send a message and create a thread to delete it after the timeout

        Args:
            context (CallbackContext): The context of the bot used to send the message
            chat_id (int): The chat where to send the message
            text (str): The message of the text
            reply_markup ([type], optional): The keyboard to send. Defaults to None.
            reply_to_message_id (int, optional): The message to reply to. Defaults to None.
            parse_mode (str, optional): How to parse the message. Defaults to "HTML".
            timeout (int, optional): The timeout after the message will be deleted. Defaults to 360.
        """
        message = context.bot.send_message(
            chat_id=chat_id,
            text=text,
            disable_web_page_preview=True,
            parse_mode=parse_mode,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
        )
        thread = threading.Thread(
            target=self.delete_message,
            args=(context, chat_id, message.message_id, timeout),
        )
        thread.start()

    def delete_if_private(self, context: CallbackContext, message: Message):
        """delete a message if it has been sent over a private chat

        Args:
            update (Update): Telegram update
            context (CallbackContext): The context of the telegram bot
            message (Message): The message to delete
        """
        if message.chat.type == "private":
            self.delete_message(context, message.chat.id, message.message_id)

    def delete_message(
        self, context: CallbackContext, chat_id: int, message_id: int, timeout: int = 0
    ):
        """Delete the message after the timeoutupdate,

        Args:
            context (CallbackContext): The context of the telegram bot
            chat_id (int): The chat where to delete the message
            message_id (int): The message to delete
            timeout (int, optional): The time to wait before deleting the message. Defaults to 0.
        """
        sleep(timeout)
        context.bot.delete_message(chat_id=chat_id, message_id=message_id)
