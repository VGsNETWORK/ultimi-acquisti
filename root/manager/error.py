#!/usr/bin/env python3

""" File to handle telegram bot api error """

import sys
import traceback
from telegram import Update
from telegram.ext import CallbackContext
from root.util.util import format_error, retrieve_key
import root.util.logger as logger
from root.contants.messages import TELEGRAM_ERROR, USER_ERROR
from root.util.telegram import TelegramSender
from root.contants.message_timeout import LONG_SERVICE_TIMEOUT

sender = TelegramSender()


def handle_error(update: Update, context: CallbackContext):
    """Send the to the log channel

    Args:
        update (Update): Telegram update
        context (CallbackContext): The context of the telegram bot
    """
    if update:
        error_channel = retrieve_key("ERROR_CHANNEL")
        if update.effective_message:
            if update.effective_chat.id != error_channel:
                update.effective_message.reply_text(USER_ERROR)
        logger.error(context.error)
        text = TELEGRAM_ERROR % format_error(context.error)
        context.bot.send_message(error_channel, text, parse_mode="HTML")
