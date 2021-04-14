#!/usr/bin/env python3

""" This File contains a class with various telegram tools """

import re
import random
from time import sleep
from os import environ
from telegram import Bot, Message, Update
from telegram.ext import CallbackContext
from telegram.error import Unauthorized, BadRequest
from pyrogram import Client
import root.util.logger as logger
from root.helper.redis_message import delete_message, message_exist
from root.helper.process_helper import create_process, stop_process
from root.helper.redis_message import add_message
from root.contants.messages import (
    BOT_NAME,
    MESSAGE_DELETION_TIMEOUT,
    MESSAGE_DELETION_FUNNY_APPEND,
    MESSAGE_EDIT_TIMEOUT,
)


def ttm(timeout: int):
    logger.info(f"parsing timeout {timeout}")
    seconds = timeout
    if timeout > 60:
        timeout = timeout // 60
        minute = "i" if timeout > 1 else "o"
        while seconds >= 60:
            seconds -= 60
        if not seconds > 0:
            return "%s %s" % (timeout, "minut%s" % minute)
        else:
            second = "i" if seconds > 1 else "o"
            return "%s %s e %s %s" % (
                timeout,
                "minut%s" % minute,
                seconds,
                "second%s" % second,
            )
    else:
        return "%s %s" % (timeout, "secondi")


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
        create_redis: bool = False,
        user_id: int = 0,
        timeout: int = 360,
        show_timeout=True,
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
        if show_timeout:
            if random.choice(range(100)) > 87:
                text += MESSAGE_DELETION_TIMEOUT % (
                    ttm(timeout),
                    random.choice(MESSAGE_DELETION_FUNNY_APPEND),
                )
            else:
                text += MESSAGE_DELETION_TIMEOUT % (ttm(timeout), "")
        else:
            text += ""
        message: Message = self._bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            disable_notification=True,
            disable_web_page_preview=True,
        )
        if create_redis:
            add_message(message.message_id, user_id, False)
        if show_timeout:
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
        # text += MESSAGE_EDIT_TIMEOUT % ttm(timeout)
        message: Message = context.bot.send_message(
            chat_id=chat_id,
            text=text,
            disable_web_page_preview=True,
            parse_mode="HTML",
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            disable_notification=True,
        )
        logger.info(f"THIS IS THE MESSAGE I SENT: {message.message_id}")
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
        if random.choice(range(100)) > 87:
            text += MESSAGE_DELETION_TIMEOUT % (
                ttm(timeout),
                random.choice(MESSAGE_DELETION_FUNNY_APPEND),
            )
        else:
            text += MESSAGE_DELETION_TIMEOUT % (ttm(timeout), "")
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

    def delete_previous_message(
        self, user_id: int, message_id: int, chat_id: int, context: CallbackContext
    ):
        logger.info(f"THIS IS {message_id}")
        payload = f"{chat_id}_{user_id}"
        previous_message_id = message_exist(payload)
        if previous_message_id:
            logger.info(f"found {previous_message_id} with payload {payload}")
            try:
                delete_message(payload)
                logger.info("deleted from Redis **")
                self.delete_message(context, chat_id, int(previous_message_id) - 1)
                logger.info("deleted from Telegram **")
                stop_process(int(previous_message_id) - 1)
                logger.info("deleted from Process **")
            except Exception as e:
                logger.error(e)
                pass
        else:
            logger.info(f"not found {previous_message_id} with payload {payload}")
        add_message(payload, message_id + 1, False)
        logger.info("added to Redis")

    def delete_if_private(self, context: CallbackContext, message: Message):
        """delete a message if it has been sent over a private chat

        Args:
            update (Update): Telegram update
            context (CallbackContext): The context of the telegram bot
            message (Message): The message to delete
        """
        self.delete_previous_message(
            message.from_user.id, message.message_id + 1, message.chat.id, context
        )
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
