#!/usr/bin/env python3

import threading
from root.util.util import db_connect
from root.manager.bot import BotManager
from root.helper.configuration import ConfigurationHelper
from root.manager.mtbot import Mtbot


"""
         I am out of here
       /
      Debug
      Debug
     De bug
    De  bug
   De   bug
  De    bug
...e    bug   Wait you can still help me 
            /  
...     bug

  Nah man, I'm good
/
...     bug

            Oh God
           /
...     bug

              Guess there's only one thing to do...
            / 
...     bug
* bug proceed to evolve into feature due to develop laziness * 
"""


def main():
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
