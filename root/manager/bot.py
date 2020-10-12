#!/usr/bin/env python3

import os
import re

from telegram import Message, Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    CallbackQueryHandler,
    Dispatcher,
    Filters,
    MessageHandler,
    Updater,
)

from root.manager.error import ErrorHandler
from root.util.util import retrieve_key, is_group_allowed
from root.manager.purchase import PurchaseManager
from root.util.logger import Logger
from root.helper.user_helper import is_admin, create_user, user_exists


class BotManager:
    def __init__(self):
        self.updater: Updater = None
        self.disp: Dispatcher = None
        self.TOKEN: str = None
        self.logger = Logger()
        self.error = ErrorHandler()
        self.purchase = PurchaseManager()

    def connect(self):
        """[run the telegram bot]"""
        self.TOKEN = retrieve_key("TOKEN")
        self.updater = Updater(self.TOKEN, use_context=True)
        self.disp = self.updater.dispatcher
        self.add_handler()
        self.logger.info("Il bot si sta avviando...")
        admin = str(retrieve_key("TELEGRAM_BOT_ADMIN"))
        self.updater.bot.send_message(
            chat_id=admin, text="Bot avviato con succcesso..."
        )
        self.updater.start_polling(clean=True)

    def restart(self, update: Update, context: CallbackContext):
        message: Message = update.message if update.message else update.edited_message
        chat_id = message.chat.id
        user_id = update.effective_user.id
        if not user_exists(user_id):
            create_user(update.effective_user)
            return
        if is_admin(user_id):
            context.bot.send_message(chat_id=chat_id, text="Riavvio il bot...")
            os.popen("sudo systemctl restart last-purchase")

    def parse_hashtag(self, update: Update, context: CallbackContext):
        message: Message = update.message if update.message else update.edited_message
        message: Message = update.message if update.message else update.edited_message
        message_text = message.caption if message.caption else message.text
        self.logger.info(f"parsing hashtag {message_text}")
        if "#ultimiacquisti" in message_text:
            self.purchase.purchase(update, context)

    def send_git_link(self, update: Update, context: CallbackContext):
        message: Message = update.message if update.message else update.edited_message
        chat_id = message.chat.id
        if not is_group_allowed(chat_id):
            return
        chat_id = update.effective_message.chat.id
        context.bot.send_message(
            chat_id=chat_id, text="https://gitlab.com/nautilor/ultimi-acquisti"
        )

    def add_handler(self):
        """[add handlers for the various operations]"""
        self.disp.add_error_handler(self.error.handle_error)
        self.disp.add_handler(CommandHandler("git", self.send_git_link))
        # self.disp.add_handler(CommandHandler("start", None))
        self.disp.add_handler(CommandHandler("restart", self.restart))
        self.disp.add_handler(
            CommandHandler("spesamensile", self.purchase.month_purchase)
        )
        self.disp.add_handler(
            CommandHandler("reportmensile", self.purchase.month_report)
        )
        self.disp.add_handler(
            CommandHandler("spesaannuale", self.purchase.year_purchase)
        )
        self.disp.add_handler(
            CommandHandler("cancellaspesa", self.purchase.delete_purchase)
        )
        self.disp.add_handler(
            CommandHandler("ultimoacquisto", self.purchase.last_purchase)
        )
        self.disp.add_handler(
            MessageHandler(Filters.caption_entity("hashtag"), self.parse_hashtag)
        )
        self.disp.add_handler(
            MessageHandler(Filters.regex("^#ultimiacquisti"), self.parse_hashtag)
        )
        self.disp.add_handler(
            CallbackQueryHandler(
                callback=self.purchase.previous_page, pattern="previous_page"
            )
        )
        self.disp.add_handler(
            CallbackQueryHandler(callback=self.purchase.next_page, pattern="next_page")
        )
        self.disp.add_handler(
            CallbackQueryHandler(
                callback=self.purchase.expand_report, pattern="expand_report"
            )
        )
