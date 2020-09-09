#!/usr/bin/env python3

from root.util.util import db_connect
from root.manager.bot import BotManager
from root.helper.configuration import ConfigurationHelper

if __name__ == "__main__":
    db_connect()
    configuation = ConfigurationHelper()
    configuation.load_configurations()
    bot = BotManager()
    bot.connect()
