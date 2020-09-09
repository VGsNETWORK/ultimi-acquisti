#!/usr/bin/env python3

from telegram import Bot
from telegram.error import Unauthorized, BadRequest
from root.util.logger import Logger

""" This class is responsible of sending messages to a channel """


class TelegramSender:
    def __init__(self):
        self._logger = Logger()
        self._token = None
        self._bot = None

    """ initialize a bot """

    def _bot_init(self, token):
        if token == self._token:
            return
        self._bot = Bot(token)
        self._token = token

    """ send message to a chat """

    def send_message(self, token, chat_id, message, **kwargs):
        self._bot_init(token)
        try:
            self._logger.info("sending message to chat {}".format(chat_id))
            self._bot.send_message(chat_id=chat_id, text=message, **kwargs)
        except Unauthorized:
            self._logger.error("403 Unauthorized, bot token is wrong")
        except BadRequest:
            self._logger.error("400 Bad Request")

    """ send photo to a chat """

    def send_photo(self, token, chat_id, photo, caption, **kwargs):
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
