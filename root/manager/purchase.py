#!/usr/bin/env python3

import re
from mongoengine.errors import DoesNotExist
from dateutil import tz
from root.util.logger import Logger
from datetime import datetime
from root.model.purchase import Purchase
from telegram import Update, Message, InlineKeyboardButton, InlineKeyboardMarkup
from root.util.util import (
    is_group_allowed,
    get_current_month,
    get_current_year,
    get_month_string,
    retrieve_key,
)
from telegram.ext import CallbackContext
from root.contants.messages import (
    PRICE_MESSAGE_NOT_FORMATTED,
    PURCHASE_ADDED,
    ONLY_GROUP,
    MONTH_PURCHASES,
    LAST_PURCHASE,
    NO_MONTH_PURCHASE,
    MONTH_PURCHASE_REPORT,
    PURCHASE_REPORT_TEMPLATE,
    YEAR_PURCHASES,
    CANCEL_PURCHASE_ERROR,
    NO_PURCHASE,
    PURCHASE_NOT_FOUND,
    PURCHASE_DELETED,
    PURCHASE_MODIFIED,
    MONTH_PURCHASE_TOTAL,
)
from root.util.telegram import TelegramSender
from root.helper.user_helper import user_exists, create_user
from root.helper.purchase_helper import (
    create_purchase,
    retrieve_sum_for_month,
    get_last_purchase,
    retrive_purchases_for_user,
    retrieve_month_purchases_for_user,
    retrieve_sum_for_current_month,
    retrieve_sum_for_current_year,
    delete_purchase,
    convert_to_float,
)


class PurchaseManager:
    def __init__(self):
        self.logger = Logger()
        self.sender = TelegramSender()
        self.month = 1
        self.current_month = 1
        self.current_year = 1970
        self.year = 1970
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
                        f"◄   {get_month_string(self.month - 1, False, False )}",
                        str(f"previous_page"),
                        "previous_page",
                    ),
                    self.create_button(
                        f" ",
                        str(f"empty_button"),
                        "empty_button",
                    ),
                    self.create_button(
                        f"{get_month_string(self.month + 1, False, False )}   ►",
                        str(f"next_page"),
                        "next_page",
                    ),
                ]
            ]
        elif not self.year == self.current_year and self.month > 1 and self.month < 12:
            keyboard = [
                [
                    self.create_button(
                        f"◄   {get_month_string(self.month - 1, False, False )}",
                        str(f"previous_page"),
                        "previous_page",
                    ),
                    self.create_button(
                        f" ",
                        str(f"empty_button"),
                        "empty_button",
                    ),
                    self.create_button(
                        f"{get_month_string(self.month + 1, False, False )}   ►",
                        str(f"next_page"),
                        "next_page",
                    ),
                ]
            ]
        elif self.month == 1:
            keyboard = [
                [
                    self.create_button(
                        f"❌",
                        str(f"empty_button"),
                        "empty_button",
                    ),
                    self.create_button(
                        f" ",
                        str(f"empty_button"),
                        "empty_button",
                    ),
                    self.create_button(
                        f"{get_month_string(self.month + 1, False, False )}   ►",
                        str(f"next_page"),
                        "next_page",
                    ),
                ]
            ]
        elif not self.year == self.current_year and self.month == 12:
            keyboard = [
                [
                    self.create_button(
                        f"◄   {get_month_string(self.month - 1, False, False )}",
                        str(f"previous_page"),
                        "previous_page",
                    ),
                    self.create_button(
                        f" ",
                        str(f"empty_button"),
                        "empty_button",
                    ),
                    self.create_button(
                        f"❌",
                        str(f"empty_button"),
                        "empty_button",
                    ),
                ]
            ]
        elif self.year == self.current_year and self.month == self.current_month:
            keyboard = [
                [
                    self.create_button(
                        f"◄   {get_month_string(self.month - 1, False, False )}",
                        str(f"previous_page"),
                        "previous_page",
                    ),
                    self.create_button(
                        f" ",
                        str(f"empty_button"),
                        "empty_button",
                    ),
                    self.create_button(
                        f"❌",
                        str(f"empty_button"),
                        "empty_button",
                    ),
                ]
            ]
        if self.year == self.current_year:
            keyboard.append(
                [
                    self.create_button(
                        f"◄   {get_month_string(self.month, True, False )} {self.year - 1}",
                        str(f"previous_year"),
                        "previous_year",
                    ),
                    self.create_button(
                        f" ",
                        str(f"empty_button"),
                        "empty_button",
                    ),
                    self.create_button(
                        f"❌",
                        str(f"empty_button"),
                        "empty_button",
                    ),
                ]
            )
        else:
            keyboard.append(
                [
                    self.create_button(
                        f"◄   {get_month_string(self.month, True, False )} {self.year - 1}",
                        str(f"previous_year"),
                        "previous_year",
                    ),
                    self.create_button(
                        f" ",
                        str(f"empty_button"),
                        "empty_button",
                    ),
                    self.create_button(
                        f"{get_month_string(self.month, True, False )} {self.year + 1}   ►",
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
                price = (f"%.2f" % purchase.price).replace(".", ",")
                creation_date = purchase.creation_date
                creation_date = creation_date.strftime(
                    f"%d {get_month_string(creation_date.month)}, %H:%M"
                )
                spaces = " " * (9 - len(price))
                template = PURCHASE_REPORT_TEMPLATE % (
                    str(purchase.chat_id).replace("-100", ""),
                    purchase.message_id,
                    creation_date,
                    spaces,
                    price,
                )
                message = f"{message}\n{template}"
            footer = retrieve_sum_for_month(user_id, self.month, self.year)
            footer = (f"%.2f" % footer).replace(".", ",")
            spaces = " " * (8 - len(footer))
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

    def last_purchase(self, update: Update, context: CallbackContext) -> None:
        message: Message = update.message if update.message else update.edited_message
        chat_id = message.chat.id
        chat_type = message.chat.type
        user = update.effective_user
        user_id = user.id
        first_name = user.first_name
        if not chat_type == "private":
            if not user_exists(user_id):
                create_user(user)
            if not is_group_allowed(chat_id):
                return
            purchase: Purchase = get_last_purchase(user_id)
        else:
            context.bot.send_message(
                chat_id=chat_id, text=ONLY_GROUP, parse_mode="HTML"
            )
            return
        if purchase:
            purchase_chat_id = str(purchase.chat_id).replace("-100", "")
            date = purchase.creation_date
            time = date.strftime("%H:%M")
            date = date.strftime("%d/%m/%Y")
            message = LAST_PURCHASE % (
                user_id,
                first_name,
                date,
                time,
                purchase_chat_id,
                purchase.message_id,
            )
        else:
            message = NO_PURCHASE % (user_id, first_name)
        context.bot.send_message(
            chat_id=chat_id,
            text=message,
            reply_to_message_id=purchase.message_id,
            parse_mode="HTML",
        )

    def purchase(self, update: Update, context: CallbackContext) -> None:
        message: Message = update.message if update.message else update.edited_message
        date = None if update.message else message.date
        self.logger.info(f"received date {date}")
        local = date.astimezone(self.to_zone) if date else None
        date = date + local.utcoffset() if date else None
        self.logger.info(f"formatted date {date}")
        chat_id = message.chat.id
        if message.chat.type == "private":
            context.bot.send_message(
                chat_id=chat_id, text=ONLY_GROUP, parse_mode="HTML"
            )
            return
        if not is_group_allowed(chat_id):
            return
        message_id = message.message_id
        user = update.effective_user
        message = message.caption if message.caption else message.text
        self.logger.info("Parsing purchase")
        try:
            """
            regex: \d+(?:[\.\',]\d{3})?(?:[\.,]\d{1,2}|[\.,]\d{1,2})?
            \d      -> matches a number
            +       -> match one or more of the previous
            ()      -> capturing group
            ?:      -> do not create a capture group (makes no sense but it does not work without)
            [\.\',] -> matches . , '
            \d{3}   -> matches 3 numbers
            ?       -> makes the capturing group optional
            ()      -> capturing group
            ?:      -> do not create a capture group (makes no sense but it does not work without)
            [\.,]   -> marches . or ,
            \d{1,2} -> matches one or two numbers
            ?       -> makes the capturing group optional
            """
            price = re.findall(r"\d+(?:[\.\',]\d{3})?(?:[\.,]\d{1,2})?", message)
            price = price[0] if len(price) != 0 else 0.00
            if price:
                price = convert_to_float(price)
                result = {"name": message, "price": price, "error": None}
                self.logger.info(f"The user purchase {price} worth of products")
            else:
                result = {"name": message, "price": 0.00, "error": None}
        except ValueError as ve:
            self.logger.error(ve)
            self.sender.send_to_log(ve)
            return
        except IndexError as ie:
            self.logger.error(ie)
            self.sender.send_to_log(ie)
            return

        if not result["error"]:
            self.add_purchase(user, price, message_id, chat_id, date)
            message = PURCHASE_ADDED if update.message else PURCHASE_MODIFIED
        else:
            message = result["error"]
        context.bot.send_message(
            chat_id=chat_id,
            text=message,
            reply_to_message_id=message_id,
            parse_mode="HTML",
        )

    def month_purchase(self, update: Update, context: CallbackContext) -> None:
        message: Message = update.message if update.message else update.edited_message
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
        price = (f"%.2f" % price).replace(".", ",")
        message = MONTH_PURCHASES % (user_id, first_name, date, price)
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
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    def year_purchase(self, update: Update, context: CallbackContext) -> None:
        message: Message = update.message if update.message else update.edited_message
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
        user_id = update.effective_user.id
        first_name = update.effective_user.first_name
        price = retrieve_sum_for_current_year(user_id)
        price = (f"%.2f" % price).replace(".", ",")
        message = YEAR_PURCHASES % (user_id, first_name, get_current_year(), price)
        self.send_purchase(update, context, price, message)

    def send_purchase(
        self, update: Update, context: CallbackContext, price: float, message: str
    ) -> None:
        telegram_message: Message = (
            update.message if update.message else update.edited_message
        )
        chat_id = telegram_message.chat.id
        context.bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")

    def add_purchase(self, user, price, message_id, chat_id, creation_date=None):
        if not user_exists(user.id):
            create_user(user)
        create_purchase(user.id, price, message_id, chat_id, creation_date)

    def delete_purchase(self, update: Update, context: CallbackContext):
        message: Message = update.message if update.message else update.edited_message
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
        message: Message = update.message if update.message else update.edited_message
        reply = message.reply_to_message
        user_id = update.effective_user.id
        chat_id = message.chat.id
        first_name = update.effective_user.first_name
        message_id = message.message_id
        if not reply:
            message = CANCEL_PURCHASE_ERROR % (user_id, first_name)
            context.bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")
            return
        try:
            message_id = reply.message_id
            delete_purchase(user_id, message_id)
            context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            context.bot.send_message(
                chat_id=chat_id, text=PURCHASE_DELETED, parse_mode="HTML"
            )
        except DoesNotExist:
            message_id = message.message_id
            message = CANCEL_PURCHASE_ERROR % (user_id, first_name)
            context.bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")
