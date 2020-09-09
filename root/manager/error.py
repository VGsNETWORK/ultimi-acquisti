#!/usr/bin/env python3

from telegram import Update
from telegram.ext import CallbackContext
from root.util.telegram import TelegramSender
from telegram import ParseMode
from root.util.util import retrieve_key
from root.util.logger import Logger
from root.contants.messages import TELEGRAM_ERROR, USER_ERROR
import sys
import traceback

class ErrorHandler:
    def __init__(self):
        super().__init__()
        self.sender = TelegramSender()
        self.logger = Logger()
    
    def handle_error(self, update: Update, context: CallbackContext):
        admin = str(retrieve_key("TELEGRAM_BOT_ADMIN"))
        if update.effective_message:
            update.effective_message.reply_text(USER_ERROR)
        trace = "".join(traceback.format_tb(sys.exc_info()[2]))
        self.logger.error(trace)
        text = TELEGRAM_ERROR % context.error
        context.bot.send_message(admin, text, parse_mode=ParseMode.HTML)