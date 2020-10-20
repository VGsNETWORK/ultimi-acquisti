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
    format_price,
)
from telegram.ext import CallbackContext
from root.contants.messages import (
    PRICE_MESSAGE_NOT_FORMATTED,
    PURCHASE_ADDED,
    ONLY_GROUP,
    MONTH_PURCHASES,
    COMPARE_HE_WON,
    YEAR_COMPARE_PRICE,
    COMPARE_YOU_WON,
    MONTH_COMPARE_PRICE,
    COMPARE_NO_PURCHASE,
    LAST_PURCHASE,
    NO_MONTH_PURCHASE,
    MONTH_USER_PURCHASES,
    MONTH_PURCHASE_REPORT,
    PURCHASE_REPORT_TEMPLATE,
    YEAR_PURCHASES,
    YEAR_USER_PURCHASES,
    CANCEL_PURCHASE_ERROR,
    NO_PURCHASE,
    PURCHASE_NOT_FOUND,
    PURCHASE_DATE_ERROR,
    PURCHASE_DELETED,
    PURCHASE_MODIFIED,
    COMPARE_TIE,
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

    def month_compare(self, update: Update, context: CallbackContext):
        message: Message = update.message if update.message else update.edited_message
        rmessage: Message = message.reply_to_message
        if not rmessage:
            return
        chat_id = message.chat.id
        ruser = rmessage.from_user
        user = message.from_user
        ruser_id = ruser.id
        user_id = user.id
        rfirst_name = ruser.first_name
        first_name = user.first_name
        upurchase = retrieve_sum_for_current_month(user_id)
        rpurchase = retrieve_sum_for_current_month(ruser_id)
        date = f"{get_current_month(False, True)} {get_current_year()}"
        message = MONTH_COMPARE_PRICE % (
            date,
            user_id,
            first_name,
            format_price(upurchase),
            rfirst_name,
            format_price(rpurchase),
        )
        if upurchase > rpurchase:
            diff = upurchase - rpurchase
            diff = format_price(diff)
            message = f"{message}{COMPARE_YOU_WON % diff}"
        elif upurchase < rpurchase:
            diff = rpurchase - upurchase
            diff = format_price(diff)
            message = f"{message}{COMPARE_HE_WON % diff}"
        else:
            if not int(rpurchase) == 0:
                message = f"{message}{COMPARE_TIE}"
            else:
                message = f"{message}{COMPARE_NO_PURCHASE}"
        context.bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")

    def year_compare(self, update: Update, context: CallbackContext):
        message: Message = update.message if update.message else update.edited_message
        rmessage: Message = message.reply_to_message
        if not rmessage:
            return
        chat_id = message.chat.id
        ruser = rmessage.from_user
        user = message.from_user
        ruser_id = ruser.id
        user_id = user.id
        rfirst_name = ruser.first_name
        first_name = user.first_name
        upurchase = retrieve_sum_for_current_year(user_id)
        rpurchase = retrieve_sum_for_current_year(ruser_id)
        message = YEAR_COMPARE_PRICE % (
            get_current_year(),
            user_id,
            first_name,
            format_price(upurchase),
            rfirst_name,
            format_price(rpurchase),
        )
        if upurchase > rpurchase:
            diff = upurchase - rpurchase
            diff = format_price(diff)
            message = f"{message}{COMPARE_YOU_WON % diff}"
        elif upurchase < rpurchase:
            diff = rpurchase - upurchase
            diff = format_price(diff)
            message = f"{message}{COMPARE_HE_WON % diff}"
        else:
            if not int(rpurchase) == 0:
                message = f"{message}{COMPARE_TIE}"
            else:
                message = f"{message}{COMPARE_NO_PURCHASE}"
        context.bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")

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
            disable_web_page_preview=True,
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
        custom_date_error = False
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

        mdate = re.findall(r"(\d(\d)?\/\d(\d)?\/\d{2}(\d{2})?)", message)
        mdate = mdate[0] if len(mdate) != 0 else None
        if mdate:
            mdate = mdate[0]
            try:
                mdate = datetime.strptime(mdate, "%d/%m/%Y")
            except ValueError:
                try:
                    mdate = datetime.strptime(mdate, "%d/%m/%y")
                except ValueError:
                    mdate = None
            if mdate:
                cdate = datetime.now()
                if mdate > cdate:
                    custom_date_error = True
                else:
                    date = mdate
            else:
                custom_date_error = True

        if not result["error"]:
            self.add_purchase(user, price, message_id, chat_id, date)
            if not custom_date_error:
                message = PURCHASE_ADDED if update.message else PURCHASE_MODIFIED
            else:
                message = PURCHASE_DATE_ERROR % (
                    user.id,
                    update.message.from_user.username,
                )
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
