#!/usr/bin/env python3

""" The bot startup file """

import threading
from root.util.util import db_connect
from root.manager.bot import BotManager
from root.helper.configuration import ConfigurationHelper
from root.manager.mtbot import Mtbot


def main():
    """ Setup the database connection, configurations and start the bot """
    db_connect()
    configuration = ConfigurationHelper()
    configuration.load_configurations()
    bot = BotManager()
    bot_thread = threading.Thread(target=bot.connect, name="mtproto")
    bot_thread.start()
    mtbot = Mtbot()
    mtbot.run()


if __name__ == "__main__":
    main()
