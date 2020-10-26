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
from root.util.util import retrieve_key, is_group_allowed, is_develop
from root.manager.purchase.month_report import MonthReport
from root.manager.purchase.year_report import YearReport
from root.manager.purchase.compare import year_compare, month_compare
from root.manager.purchase.month_purchase import month_purchase
from root.manager.purchase.year_purchase import year_purchase
from root.manager.purchase.last import last_purchase
from root.manager.purchase.delete import delete_purchase
from root.util.logger import Logger
from root.helper.user_helper import is_admin, create_user, user_exists
from root.util.telegram import TelegramSender


class BotManager:
    def __init__(self):
        self.updater: Updater = None
        self.disp: Dispatcher = None
        self.TOKEN: str = None
        self.logger = Logger()
        self.sender = TelegramSender()
        self.error = ErrorHandler()
        self.month_report = MonthReport()
        self.year_report = YearReport()

    def connect(self):
        """[run the telegram bot]"""
        self.TOKEN = retrieve_key("TOKEN")
        self.updater = Updater(self.TOKEN, use_context=True)
        self.disp = self.updater.dispatcher
        self.add_handler()
        self.logger.info("Il bot si sta avviando...")
        admin = str(retrieve_key("TELEGRAM_BOT_ADMIN"))
        self.logger.info("Start polling...")
        self.updater.start_polling(clean=True)

    def restart(self, update: Update, context: CallbackContext):
        message: Message = update.message if update.message else update.edited_message
        chat_id = message.chat.id
        user_id = update.effective_user.id
        if not user_exists(user_id):
            create_user(update.effective_user)
            return
        if is_admin(user_id):
            self.sender.send_and_delete(
                context, chat_id, "Riavvio il bot...", timeout=10
            )
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
        self.sender.send_and_delete(
            context, chat_id=chat_id, text="https://gitlab.com/nautilor/ultimi-acquisti"
        )

    def empty_button(self, update: Update, context: CallbackContext):
        context.bot.answer_callback_query(update.callback_query.id)

    def add_handler(self):
        """[add handlers for the various operations]"""
        self.disp.add_error_handler(self.error.handle_error)
        self.disp.add_handler(CommandHandler("git", self.send_git_link))
        self.disp.add_handler(CommandHandler("restart", self.restart))
        self.disp.add_handler(CommandHandler("cancellaspesa", delete_purchase))
        self.disp.add_handler(CommandHandler("ultimoacquisto", last_purchase))
        self.disp.add_handler(CommandHandler("comparamese", month_compare))
        self.disp.add_handler(CommandHandler("comparaanno", year_compare))
        self.disp.add_handler(CommandHandler("spesaannuale", year_purchase))
        self.disp.add_handler(CommandHandler("spesamensile", month_purchase))

        self.disp.add_handler(
            CommandHandler("reportannuale", self.year_report.year_report)
        )
        self.disp.add_handler(
            CallbackQueryHandler(
                callback=self.year_report.previous_year, pattern="year_previous_year"
            )
        )
        self.disp.add_handler(
            CallbackQueryHandler(
                callback=self.year_report.next_year, pattern="year_next_year"
            )
        )

        self.disp.add_handler(
            CommandHandler("reportmensile", self.month_report.month_report)
        )
        self.disp.add_handler(
            CallbackQueryHandler(
                callback=self.month_report.previous_page, pattern="month_previous_page"
            )
        )
        self.disp.add_handler(
            CallbackQueryHandler(
                callback=self.month_report.next_page, pattern="month_next_page"
            )
        )
        self.disp.add_handler(
            CallbackQueryHandler(
                callback=self.month_report.next_year, pattern="month_next_year"
            )
        )
        self.disp.add_handler(
            CallbackQueryHandler(
                callback=self.month_report.previous_year, pattern="month_previous_year"
            )
        )
        self.disp.add_handler(
            CallbackQueryHandler(
                callback=self.month_report.next_start_year,
                pattern="month_next_start_year",
            )
        )
        self.disp.add_handler(
            CallbackQueryHandler(
                callback=self.month_report.previous_start_year,
                pattern="month_previous_start_year",
            )
        )
        self.disp.add_handler(
            CallbackQueryHandler(callback=self.empty_button, pattern="empty_button")
        )
        self.disp.add_handler(
            CallbackQueryHandler(
                callback=self.month_report.expand_report, pattern="expand_report"
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                callback=self.year_report.expand_report, pattern="expand_year_report"
            )
        )
