#!/usr/bin/env python3

""" File to handle telegram bot api error """

import sys
import traceback
from telegram import Update
from telegram.ext import CallbackContext
from root.util.util import retrieve_key
import root.util.logger as logger
from root.contants.messages import TELEGRAM_ERROR, USER_ERROR


def handle_error(update: Update, context: CallbackContext):
    """Send the to the log channel

    Args:
        update (Update): Telegram update
        context (CallbackContext): The context of the telegram bot
    """
    chat_id = retrieve_key("ERROR_CHANNEL")
    if update.effective_message:
        update.effective_message.reply_text(USER_ERROR)
    trace = "".join(traceback.format_tb(sys.exc_info()[2]))
    logger.error(trace)
    text = TELEGRAM_ERROR % context.error
    context.bot.send_message(chat_id, text, parse_mode="HTML")
