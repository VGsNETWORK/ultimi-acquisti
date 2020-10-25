#!/usr/bin/env python3

from datetime import datetime

from dateutil import tz
from telegram import InlineKeyboardMarkup, Message, Update
from telegram.ext import CallbackContext
from root.contants.messages import (
    YEAR_PURCHASE_REPORT,
    REPORT_PURCHASE_TOTAL,
    NO_MONTH_PURCHASE,
    PURCHASE_REPORT_TEMPLATE,
    YEAR_PURCHASE_TEMPLATE,
)
from root.helper.purchase_helper import retrieve_sum_for_month, retrieve_sum_for_year
from root.helper.user_helper import create_user, user_exists
from root.util.logger import Logger
from root.util.telegram import TelegramSender
from root.util.util import (
    create_button,
    format_price,
    get_month_string,
    is_group_allowed,
)


class YearReport:
    def __init__(self):
        self.logger = Logger()
        self.sender = TelegramSender()
        current_date = datetime.now()
        self.month = current_date.month
        self.current_month = current_date.month
        self.current_year = current_date.year
        self.year = current_date.year
        self.to_zone = tz.gettz("Europe/Rome")

    def year_report(
        self, update: Update, context: CallbackContext, expand: bool = False
    ) -> None:
        current_date = datetime.now()
        self.month = current_date.month
        self.current_month = current_date.month
        self.year = current_date.year
        self.current_year = current_date.year
        message: Message = update.message if update.message else update.edited_message
        if not message:
            context.bot.answer_callback_query(update.callback_query.id)
            message = update.effective_message
        chat_id = message.chat.id
        chat_type = message.chat.type
        user = update.effective_user
        user_id = user.id
        message_id = message.message_id
        if not chat_type == "private":
            if not user_exists(user_id):
                create_user(user)
            if not is_group_allowed(chat_id):
                return
        keyboard = self.build_keyboard()
        message = self.retrieve_purchase(user)
        if expand:
            context.bot.edit_message_text(
                text=message,
                chat_id=chat_id,
                disable_web_page_preview=True,
                message_id=message_id,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="HTML",
            )
            return
        context.bot.send_message(
            chat_id=chat_id,
            text=message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
        )

    def expand_report(self, update: Update, context: CallbackContext) -> None:
        self.month_report(update, context, True)

    def build_keyboard(self):
        keyboard = []
        if self.year == self.current_year:
            keyboard = [
                [
                    create_button(
                        f"{self.year - 1}   ◄",
                        str("year_previous_year"),
                        "year_previous_year",
                    ),
                    create_button(
                        f"{self.year}",
                        str("empty_button"),
                        "empty_button",
                    ),
                    create_button(
                        "🔚",
                        str("empty_button"),
                        "empty_button",
                    ),
                ]
            ]
        else:
            keyboard = [
                [
                    create_button(
                        f"{self.year - 1}   ◄",
                        str("year_previous_year"),
                        "year_previous_year",
                    ),
                    create_button(
                        f"{self.year}",
                        str("empty_button"),
                        "empty_button",
                    ),
                    create_button(
                        f"►   {self.year + 1}",
                        str("year_next_year"),
                        "year_next_year",
                    ),
                ]
            ]
        return keyboard

    def retrieve_purchase(self, user):
        user_id = user.id
        first_name = user.first_name
        purchases = [
            retrieve_sum_for_month(user_id, i, self.year) for i in range(1, 13)
        ]
        if not purchases:
            message = NO_YEAR_PURCHASE % (user_id, first_name, self.year)
        else:
            message = YEAR_PURCHASE_REPORT % (user_id, first_name, self.year)
            for i in range(0, 12):
                price = format_price(purchases[i])
                month = get_month_string(i + 1, False)
                spaces = 11 - len(price)
                spaces += 9 - len(month)
                spaces = " " * spaces
                template = YEAR_PURCHASE_TEMPLATE % (
                    month,
                    spaces,
                    price,
                )
                message = f"{message}\n{template}"
            footer = retrieve_sum_for_year(user_id, self.year)
            footer = format_price(footer)
            spaces = " " * (10 - len(footer))
            footer = REPORT_PURCHASE_TOTAL % (spaces, footer)
            message = f"{message}\n\n{footer}"
        return message

    def previous_year(self, update: Update, context: CallbackContext):
        context.bot.answer_callback_query(update.callback_query.id)
        self.year -= 1
        user = update.effective_user
        message = self.retrieve_purchase(user)
        keyboard = self.build_keyboard()
        message_id = update.effective_message.message_id
        chat_id = update.effective_chat.id
        context.bot.edit_message_text(
            text=message,
            chat_id=chat_id,
            disable_web_page_preview=True,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
        )

    def next_year(self, update: Update, context: CallbackContext):
        context.bot.answer_callback_query(update.callback_query.id)
        self.year += 1
        if self.year >= self.current_year:
            self.year = self.current_year
        user = update.effective_user
        message = self.retrieve_purchase(user)
        keyboard = self.build_keyboard()
        message_id = update.effective_message.message_id
        chat_id = update.effective_chat.id
        context.bot.edit_message_text(
            text=message,
            chat_id=chat_id,
            disable_web_page_preview=True,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
        )
