#!/usr/bin/env python3


import re
from telegram import Update, Message, User
from telegram.ext import CallbackContext
from root.manager.help import bot_help
from root.util.telegram import TelegramSender

sender = TelegramSender()


def handle_params(update: Update, context: CallbackContext, params: str) -> None:
    """handle various params recevied during the /start command

    Args:
        update (Update): Telegram update
        context (CallbackContext): The context of the telegram bot
        params (str): the params passed to the /start command
    """
    if params == "how_to":
        bot_help(update, context)
    return


def handle_start(update: Update, context: CallbackContext) -> None:
    """Handle the command /start from the user along with some query params

    Args:
        update (Update): Telegram update
        context (CallbackContext): The context of the telegram bot
    """
    message: Message = update.message if update.message else update.edited_message
    sender.delete_if_private(context, message)
    params = re.sub("\\/\\w+\\s", "", message.text)
    if params:
        handle_params(update, context, params)
        return
