#!/usr/bin/env python3

import re
from datetime import datetime

from dateutil import tz
from mongoengine.errors import DoesNotExist
from root.contants.messages import (
    CANCEL_PURCHASE_ERROR,
    COMPARE_HE_WON,
    COMPARE_NO_PURCHASE,
    COMPARE_TIE,
    COMPARE_YOU_WON,
    LAST_PURCHASE,
    MONTH_COMPARE_PRICE,
    MONTH_PURCHASE_REPORT,
    MONTH_PURCHASE_TOTAL,
    MONTH_PURCHASES,
    MONTH_USER_PURCHASES,
    NO_MONTH_PURCHASE,
    NO_PURCHASE,
    ONLY_GROUP,
    PRICE_MESSAGE_NOT_FORMATTED,
    PURCHASE_ADDED,
    PURCHASE_DATE_ERROR,
    PURCHASE_DELETED,
    PURCHASE_MODIFIED,
    PURCHASE_NOT_FOUND,
    PURCHASE_REPORT_TEMPLATE,
    YEAR_COMPARE_PRICE,
    YEAR_PURCHASES,
    YEAR_USER_PURCHASES,
)
from root.helper.purchase_helper import (
    convert_to_float,
    create_purchase,
    delete_purchase,
    get_last_purchase,
    retrieve_month_purchases_for_user,
    retrieve_sum_for_current_month,
    retrieve_sum_for_current_year,
    retrieve_sum_for_month,
    retrive_purchases_for_user,
)
from root.helper.user_helper import create_user, user_exists
from root.model.purchase import Purchase
from root.util.logger import Logger
from root.util.telegram import TelegramSender
from root.util.util import (
    format_price,
    get_current_month,
    get_current_year,
    get_month_string,
    is_group_allowed,
    retrieve_key,
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, Update
from telegram.ext import CallbackContext

""" TODO: 
    - Rifattorizzare il codice togliendo le ripetizioni di codice e migliorando dove possibile
    - Dividere le varie funzionalità in file diversi in modo da snellire le quasi 1000 righe di codice
    - Il comparamese/comparaanno posso avere in input rispettivamente mese/anno o anno per fare comparazioni al di fuori di anno/mese corrente
    - Quando viene inserita la data manuale per acquisto nel caso sia formatta male o futura chiedere conferma all'utente riguardo l'inserimento a data attuale
    - Breakdance
"""


class PurchaseManager:
    def __init__(self):
        self.logger = Logger()
        self.sender = TelegramSender()
        current_date = datetime.now()
        self.month = current_date.month
        self.current_month = current_date.month
        self.current_year = current_date.year
        self.year = current_date.year
        self.to_zone = tz.gettz("Europe/Rome")

    def month_report(
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
            message = update._effective_message
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
        if (
            self.year == self.current_year
            and self.month > 1
            and self.month < self.current_month
        ):
            keyboard = [
                [
                    self.create_button(
                        f"{get_month_string(self.month - 1, False, False )}   ◄",
                        str(f"previous_page"),
                        "previous_page",
                    ),
                    self.create_button(
                        f"{get_month_string(self.month, False, False).upper()}",
                        str(f"empty_button"),
                        "empty_button",
                    ),
                    self.create_button(
                        f"►   {get_month_string(self.month + 1, False, False )}",
                        str(f"next_page"),
                        "next_page",
                    ),
                ]
            ]
        elif not self.year == self.current_year and self.month > 1 and self.month < 12:
            keyboard = [
                [
                    self.create_button(
                        f"{get_month_string(self.month - 1, False, False )}   ◄",
                        str(f"previous_page"),
                        "previous_page",
                    ),
                    self.create_button(
                        f"{get_month_string(self.month, False, False).upper()}",
                        str(f"empty_button"),
                        "empty_button",
                    ),
                    self.create_button(
                        f"►   {get_month_string(self.month + 1, False, False )}",
                        str(f"next_page"),
                        "next_page",
                    ),
                ]
            ]
        elif self.month == 1:
            message = f"{get_month_string(12, True, False )} {self.year - 1}   ◄"
            keyboard = [
                [
                    self.create_button(
                        f"{message}",
                        str(f"previous_start_year"),
                        "previous_start_year",
                    ),
                    self.create_button(
                        f"{get_month_string(self.month, False, False).upper()}",
                        str(f"empty_button"),
                        "empty_button",
                    ),
                    self.create_button(
                        f"►   {get_month_string(self.month + 1, False, False )}",
                        str(f"next_page"),
                        "next_page",
                    ),
                ]
            ]
        elif not self.year == self.current_year and self.month == 12:
            message = f"►   {get_month_string(1, True, False )} {self.year + 1}"
            keyboard = [
                [
                    self.create_button(
                        f"{get_month_string(self.month - 1, False, False )}   ◄",
                        str(f"previous_page"),
                        "previous_page",
                    ),
                    self.create_button(
                        f"{get_month_string(self.month, False, False).upper()}",
                        str(f"empty_button"),
                        "empty_button",
                    ),
                    self.create_button(
                        f"{message}",
                        str(f"next_start_year"),
                        "next_start_year",
                    ),
                ]
            ]
        elif self.year == self.current_year and self.month == self.current_month:
            keyboard = [
                [
                    self.create_button(
                        f"{get_month_string(self.month - 1, False, False )}   ◄",
                        str(f"previous_page"),
                        "previous_page",
                    ),
                    self.create_button(
                        f"{get_month_string(self.month, False, False).upper()}",
                        str(f"empty_button"),
                        "empty_button",
                    ),
                    self.create_button(
                        f"🔚",
                        str(f"empty_button"),
                        "empty_button",
                    ),
                ]
            ]
        if self.year == self.current_year:
            keyboard.append(
                [
                    self.create_button(
                        f"{get_month_string(self.month, True, False )} {self.year - 1}   ◄",
                        str(f"previous_year"),
                        "previous_year",
                    ),
                    self.create_button(
                        f"{self.year}",
                        str(f"empty_button"),
                        "empty_button",
                    ),
                    self.create_button(
                        f"🔚",
                        str(f"empty_button"),
                        "empty_button",
                    ),
                ]
            )
        else:
            if self.year + 1 == self.current_year and self.month > self.current_month:
                month = self.current_month
            else:
                month = self.month
            keyboard.append(
                [
                    self.create_button(
                        f"{get_month_string(self.month, True, False )} {self.year - 1}   ◄",
                        str(f"previous_year"),
                        "previous_year",
                    ),
                    self.create_button(
                        f"{self.year}",
                        str(f"empty_button"),
                        "empty_button",
                    ),
                    self.create_button(
                        f"►   {get_month_string(month, True, False )} {self.year + 1}",
                        str(f"next_year"),
                        "next_year",
                    ),
                ]
            )
        return keyboard

    def retrieve_purchase(self, user):
        if self.month > 12:
            self.month = 12
        if self.month < 1:
            self.month = 1
        user_id = user.id
        first_name = user.first_name
        purchases = retrieve_month_purchases_for_user(user_id, self.month, self.year)
        date = f"{get_month_string(self.month, False, True)} {self.year}"
        if not purchases:
            message = NO_MONTH_PURCHASE % (user_id, first_name, date)
        else:
            message = MONTH_PURCHASE_REPORT % (user_id, first_name, date)
            for purchase in purchases:
                price = format_price(purchase.price)
                creation_date = purchase.creation_date
                creation_date = creation_date.strftime(
                    f"%d {get_month_string(creation_date.month)}, %H:%M"
                )
                spaces = " " * (11 - len(price))
                template = PURCHASE_REPORT_TEMPLATE % (
                    str(purchase.chat_id).replace("-100", ""),
                    purchase.message_id,
                    creation_date,
                    spaces,
                    price,
                )
                message = f"{message}\n{template}"
            footer = retrieve_sum_for_month(user_id, self.month, self.year)
            footer = format_price(footer)
            spaces = " " * (10 - len(footer))
            footer = MONTH_PURCHASE_TOTAL % (spaces, footer)
            message = f"{message}\n\n{footer}"
        return message

    def previous_page(self, update: Update, context: CallbackContext):
        context.bot.answer_callback_query(update.callback_query.id)
        self.month -= 1
        user = update.effective_user
        message = self.retrieve_purchase(user)
        keyboard = self.build_keyboard()
        message_id = update._effective_message.message_id
        chat_id = update._effective_chat.id
        context.bot.edit_message_text(
            text=message,
            chat_id=chat_id,
            disable_web_page_preview=True,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
        )

    def next_page(self, update: Update, context: CallbackContext):
        context.bot.answer_callback_query(update.callback_query.id)
        self.month += 1
        user = update.effective_user
        message = self.retrieve_purchase(user)
        keyboard = self.build_keyboard()
        message_id = update._effective_message.message_id
        chat_id = update._effective_chat.id
        context.bot.edit_message_text(
            text=message,
            chat_id=chat_id,
            disable_web_page_preview=True,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
        )

    def previous_year(self, update: Update, context: CallbackContext):
        context.bot.answer_callback_query(update.callback_query.id)
        self.year -= 1
        user = update.effective_user
        message = self.retrieve_purchase(user)
        keyboard = self.build_keyboard()
        message_id = update._effective_message.message_id
        chat_id = update._effective_chat.id
        context.bot.edit_message_text(
            text=message,
            chat_id=chat_id,
            disable_web_page_previewsend_purchase=True,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
        )

    def next_start_year(self, update: Update, context: CallbackContext):
        context.bot.answer_callback_query(update.callback_query.id)
        self.year += 1
        self.month = 1
        if self.year == self.current_year:
            if self.month > self.current_month:
                self.month = self.current_month
        if self.year > self.current_year:
            self.year = self.current_year
        user = update.effective_user
        message = self.retrieve_purchase(user)
        keyboard = self.build_keyboard()
        message_id = update._effective_message.message_id
        chat_id = update._effective_chat.id
        context.bot.edit_message_text(
            text=message,
            chat_id=chat_id,
            disable_web_page_preview=True,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
        )

    def previous_start_year(self, update: Update, context: CallbackContext):
        context.bot.answer_callback_query(update.callback_query.id)
        self.year -= 1
        self.month = 12
        if self.year == self.current_year:
            if self.month > self.current_month:
                self.month = self.current_month
        if self.year > self.current_year:
            self.year = self.current_year
        user = update.effective_user
        message = self.retrieve_purchase(user)
        keyboard = self.build_keyboard()
        message_id = update._effective_message.message_id
        chat_id = update._effective_chat.id
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
        if self.year == self.current_year:
            if self.month > self.current_month:
                self.month = self.current_month
        if self.year > self.current_year:
            self.year = self.current_year
        user = update.effective_user
        message = self.retrieve_purchase(user)
        keyboard = self.build_keyboard()
        message_id = update._effective_message.message_id
        chat_id = update._effective_chat.id
        context.bot.edit_message_text(
            text=message,
            chat_id=chat_id,
            disable_web_page_preview=True,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
        )

    def create_button(self, message: str, callback: str, query: str):
        return InlineKeyboardButton(message, callback_data=callback)

    def month_purchase(self, update: Update, context: CallbackContext) -> None:
        message: Message = update.message if update.message else update.edited_message
        template: str = (
            MONTH_USER_PURCHASES if message.reply_to_message else MONTH_PURCHASES
        )
        expand = False if message.reply_to_message else True
        message = message.reply_to_message if message.reply_to_message else message
        chat_id = message.chat.id
        chat_type = message.chat.type
        user = message.from_user
        user_id = user.id
        first_name = user.first_name
        if not chat_type == "private":
            if not user_exists(user_id):
                create_user(user)
            if not is_group_allowed(chat_id):
                return
        price = retrieve_sum_for_current_month(user_id)
        date = f"{get_current_month( False, True)} {get_current_year()}"
        price = format_price(price)
        message = template % (user_id, first_name, date, price)
        telegram_message: Message = (
            update.message if update.message else update.edited_message
        )
        chat_id = telegram_message.chat.id
        keyboard = [
            [self.create_button("Espandi", str(f"expand_report"), "expand_report")]
        ]
        context.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard) if expand else None,
        )

    def year_purchase(self, update: Update, context: CallbackContext) -> None:
        message: Message = update.message if update.message else update.edited_message
        template: str = (
            YEAR_USER_PURCHASES if message.reply_to_message else YEAR_PURCHASES
        )
        message = message.reply_to_message if message.reply_to_message else message
        chat_id = message.chat.id
        user = message.from_user
        user_id = user.id
        first_name = user.first_name
        chat_type = message.chat.type
        if not chat_type == "private":
            if not user_exists(user_id):
                create_user(user)
            if not is_group_allowed(chat_id):
                return
        price = retrieve_sum_for_current_year(user_id)
        price = format_price(price)
        message = template % (user_id, first_name, get_current_year(), price)
        self.send_purchase(update, context, price, message)

    def send_purchase(
        self, update: Update, context: CallbackContext, price: float, message: str
    ) -> None:
        telegram_message: Message = (
            update.message if update.message else update.edited_message
        )
        chat_id = telegram_message.chat.id
        context.bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")
