#!/usr/bin/env python3

""" The bot startup file """

import threading
from root.util.util import db_connect
from root.manager.bot import BotManager
from root.helper.configuration import ConfigurationHelper
from root.manager.mtbot import Mtbot
from root.helper.redis_message import reset_redis
from telegram_utils.utils.misc import environment
from time import sleep
from bot_util.util.database import connect
from bot_util.helper.bot_status import update_status


def main():
    """Setup the database connection, configurations and start the bot"""
    reset_redis()
    db_connect()
    connect()
    reputation = environment("REPUTATION_DB")
    configuration = ConfigurationHelper()
    configuration.load_configurations()
    bot = BotManager()
    bot_thread = threading.Thread(target=bot.connect, name="bot-api")
    bot_thread.start()
    mtbot = Mtbot()
    mtbot.run_userbot()
    mtbot.run_bot()


if __name__ == "__main__":
    main()
