#!/usr/bin/env python3

""" This File contains a class with various telegram tools """

import re
from time import sleep
from os import environ
from telegram import Bot, Message, Update
from telegram.ext import CallbackContext
from telegram.error import Unauthorized, BadRequest
from pyrogram import Client
from pyrogram.types import Message as ProtoMessage
import root.util.logger as logger
from root.helper.redis_message import delete_message
from root.helper.process_helper import create_process
from root.helper.redis_message import add_message
from root.contants.messages import BOT_NAME


class TelegramSender:
    """ This class contains a class with various telegram tools """

    def __init__(self):
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

    def check_command(self, message: Message):
        if message.chat.type != "private":
            command: str = message.text
            command: str = re.sub(r"/\w+", "", command)
            if f"@{BOT_NAME}" in command:
                return True
            return False
        else:
            return True

    def send_message(self, token: str, chat_id: int, message: str, **kwargs):
        """send a message to a designed chat

        Args:
            token (str): Telegram token of the bot
            chat_id (int): The chat where to send the message
            message (str): The message to send
        """
        self._bot_init(token)
        try:
            self._bot = Bot(environ["TOKEN"])
            print("TOKEN")
            print(environ["TOKEN"])
            logger.info("sending message to chat {}".format(chat_id))
            self._bot.send_message(chat_id=chat_id, text=message, **kwargs)
        except Unauthorized as unauthorized_exception:
            print(unauthorized_exception)
            logger.error("403 Unauthorized, bot token is wrong")
        except BadRequest:
            logger.error("400 Bad Request")

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
            self._bot = Bot(environ["TOKEN"])
            logger.info("sending photo to chat {}".format(chat_id))
            self._bot.send_photo(
                chat_id=chat_id, photo=photo, caption=caption, **kwargs
            )
        except Unauthorized:
            logger.error("403 Unauthorized, bot token is wrong")
        except BadRequest:
            logger.error("400 Bad Request")

    def send_and_deproto(
        self,
        client: Client,
        chat_id: int,
        text: str,
        reply_markup=None,
        reply_to_message_id: int = None,
        parse_mode: str = "HTML",
        timeout: int = 360,
    ):
        """Send a message and create a thread to delete it after the timeout

        Args:
            client (Client): The mtproto bot instance
            chat_id (int): The chat where to send the message
            text (str): The text of the message
            reply_to_message_id (int, optional): The message to reply to. Defaults to None.
            parse_mode (str, optional): How to parse the message. Defaults to "HTML".
            timeout (int, optional): [description]. Defaults to 360.
        """
        self._bot = Bot(environ["TOKEN"])
        message: Message = self._bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            disable_notification=True,
        )
        create_process(
            name_prefix=message.message_id,
            target=self.delete_message,
            args=(client, chat_id, message.message_id, timeout),
        )

    def send_and_edit(
        self,
        update: Update,
        context: CallbackContext,
        chat_id: int,
        text: str,
        callback,
        reply_markup=None,
        reply_to_message_id: int = None,
        timeout=360,
    ):
        message: Message = context.bot.send_message(
            chat_id=chat_id,
            text=text,
            disable_web_page_preview=True,
            parse_mode="HTML",
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            disable_notification=True,
        )
        create_process(
            name_prefix=message.message_id,
            target=callback,
            args=(update, context, chat_id, message.message_id, timeout),
        )

    def send_and_delete(
        self,
        original_message: int,
        user_id: int,
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
            text (str): The text of the message
            reply_markup ([type], optional): The keyboard to send. Defaults to None.
            reply_to_message_id (int, optional): The message to reply to. Defaults to None.
            parse_mode (str, optional): How to parse the message. Defaults to "HTML".
            timeout (int, optional): The timeout after the message will be deleted. Defaults to 360.
        """
        message: Message = context.bot.send_message(
            chat_id=chat_id,
            text=text,
            disable_web_page_preview=True,
            parse_mode=parse_mode,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            disable_notification=True,
        )
        create_process(
            name_prefix=message.message_id,
            target=self.delete_message,
            args=(context, chat_id, message.message_id, timeout),
        )

    def delete_if_private(self, context: CallbackContext, message: Message):
        """delete a message if it has been sent over a private chat

        Args:
            update (Update): Telegram update
            context (CallbackContext): The context of the telegram bot
            message (Message): The message to delete
        """
        if message.chat.type == "private":
            self.delete_message(
                context,
                message.chat.id,
                message.message_id,
            )

    def delete_message(
        self, context: CallbackContext, chat_id: int, message_id: int, timeout: int = 0
    ):
        """Delete the message after the timeoutupdate,

        Argsprint:
            context (CallbackContext): The context of the telegram bot
            chat_id (int): The chat where to delete the message
            message_id (int): The message to delete
            timeout (int, optional): The time to wait before deleting the message. Defaults to 0.
        """
        sleep(timeout)
        try:
            logger.info(f"deleting {message_id} from redis")
            delete_message(message_id)
            logger.info(f"deleting {message_id} from telegram")
            self._bot = Bot(environ["TOKEN"])
            self._bot.delete_message(chat_id=chat_id, message_id=message_id)
        except BadRequest:
            pass

    def deproto_message(
        self, client: Client, chat_id: int, message_id: int, timeout: int = 0
    ):
        """Delete the message after the timeoutupdate,

        Args:
            client (Client): The mtproto bot instance
            chat_id (int): The chat where to delete the message
            message_id (int): The message to delete
            timeout (int, optional): The time to wait before deleting the message. Defaults to 0.
        """
        sleep(timeout)
        try:
            logger.info(f"deleting {message_id} from redis")
            delete_message(message_id)
            logger.info(f"deleting {message_id} from telegram")
            self._bot = Bot(environ["TOKEN"])
            self._bot.delete_message(chat_id=chat_id, message_id=message_id)
        except BadRequest:
            pass
