#!/usr/bin/env python3

from root.util.util import db_connect
from root.manager.bot import BotManager
from root.helper.configuration import ConfigurationHelper


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
* bug proceed to evolve into feature due to develop laziness* 
"""

if __name__ == "__main__":
    db_connect()
    configuation = ConfigurationHelper()
    configuation.load_configurations()
    bot = BotManager()
    bot.connect()
