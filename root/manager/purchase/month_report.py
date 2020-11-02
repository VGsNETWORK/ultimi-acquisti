#!/usr/bin/env python3

""" File with class to show the month report """

from datetime import datetime
from dateutil import tz
from telegram import InlineKeyboardMarkup, Message, Update, InlineKeyboardButton, User
from telegram.ext import CallbackContext
from root.helper.redis_message import add_message, is_owner
from root.model.purchase import Purchase
from root.contants.messages import (
    MONTH_PURCHASE_REPORT,
    REPORT_PURCHASE_TOTAL,
    NO_MONTH_PURCHASE,
    PURCHASE_REPORT_TEMPLATE,
    NOT_MESSAGE_OWNER,
)
from root.helper.purchase_helper import (
    retrieve_month_purchases_for_user,
    retrieve_sum_for_month,
)
from root.helper.user_helper import create_user, user_exists
from root.util.logger import Logger
from root.util.telegram import TelegramSender
from root.util.util import (
    create_button,
    format_price,
    get_month_string,
    is_group_allowed,
)


class MonthReport:
    """ Class used to display the month report of a user """

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
        """Show the month report of a user

        Args:
            update (Update): Telegram update
            context (CallbackContext): The context of the telegram bot
            expand (bool, optional): if the call comes from a purchase message. Defaults to False.
        """
        current_date = datetime.now()
        self.month = current_date.month
        self.current_month = current_date.month
        self.year = current_date.year
        self.current_year = current_date.year
        message: Message = update.message if update.message else update.edited_message
        if not message:
            message = update.effective_message
        else:
            self.sender.delete_if_private(context, message)
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
            if is_owner(message_id, user_id):
                context.bot.answer_callback_query(update.callback_query.id)
                context.bot.edit_message_text(
                    text=message,
                    chat_id=chat_id,
                    disable_web_page_preview=True,
                    message_id=message_id,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="HTML",
                )
            else:
                context.bot.answer_callback_query(
                    update.callback_query.id, text=NOT_MESSAGE_OWNER, show_alert=True
                )
            return
        add_message(message_id, user_id)
        self.sender.send_and_delete(
            context, chat_id, message, InlineKeyboardMarkup(keyboard), timeout=300
        )

    def expand_report(self, update: Update, context: CallbackContext) -> None:
        """The callback to indicate to expand the month purchase message into the report

        Args:
            update (Update): Telegram update
            context (CallbackContext): The context of the telegram bot
        """
        self.month_report(update, context, True)

    def build_keyboard(self) -> [[InlineKeyboardButton]]:
        """Create the keyboard for the report

        Returns:
            [[InlineKeyboardButton]]: Array of Arrays of Keyboard Buttons
        """
        keyboard = []
        if (
            self.year == self.current_year
            and self.month > 1
            and self.month < self.current_month
        ):
            keyboard = [
                [
                    create_button(
                        f"{get_month_string(self.month - 1, False, False )}   ◄",
                        str("month_previous_page"),
                        "month_previous_page",
                    ),
                    create_button(
                        f"{get_month_string(self.month, False, False).upper()}",
                        str("empty_button"),
                        "empty_button",
                    ),
                    create_button(
                        f"►   {get_month_string(self.month + 1, False, False )}",
                        str("month_next_page"),
                        "month_next_page",
                    ),
                ]
            ]
        elif not self.year == self.current_year and self.month > 1 and self.month < 12:
            keyboard = [
                [
                    create_button(
                        f"{get_month_string(self.month - 1, False, False )}   ◄",
                        str("month_previous_page"),
                        "month_previous_page",
                    ),
                    create_button(
                        f"{get_month_string(self.month, False, False).upper()}",
                        str("empty_button"),
                        "empty_button",
                    ),
                    create_button(
                        f"►   {get_month_string(self.month + 1, False, False )}",
                        str("month_next_page"),
                        "month_next_page",
                    ),
                ]
            ]
        elif self.month == 1:
            message = f"{get_month_string(12, True, False )} {self.year - 1}   ◄"
            keyboard = [
                [
                    create_button(
                        f"{message}",
                        str("month_previous_start_year"),
                        "month_previous_start_year",
                    ),
                    create_button(
                        f"{get_month_string(self.month, False, False).upper()}",
                        str("empty_button"),
                        "empty_button",
                    ),
                    create_button(
                        f"►   {get_month_string(self.month + 1, False, False )}",
                        str("month_next_page"),
                        "month_next_page",
                    ),
                ]
            ]
        elif not self.year == self.current_year and self.month == 12:
            message = f"►   {get_month_string(1, True, False )} {self.year + 1}"
            keyboard = [
                [
                    create_button(
                        f"{get_month_string(self.month - 1, False, False )}   ◄",
                        str("month_previous_page"),
                        "month_previous_page",
                    ),
                    create_button(
                        f"{get_month_string(self.month, False, False).upper()}",
                        str("empty_button"),
                        "empty_button",
                    ),
                    create_button(
                        f"{message}",
                        str("month_next_start_year"),
                        "month_next_start_year",
                    ),
                ]
            ]
        elif self.year == self.current_year and self.month == self.current_month:
            keyboard = [
                [
                    create_button(
                        f"{get_month_string(self.month - 1, False, False )}   ◄",
                        str("month_previous_page"),
                        "month_previous_page",
                    ),
                    create_button(
                        f"{get_month_string(self.month, False, False).upper()}",
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
        if self.year == self.current_year:
            keyboard.append(
                [
                    create_button(
                        f"{get_month_string(self.month, True, False )} {self.year - 1}   ◄",
                        str("month_previous_year"),
                        "month_previous_year",
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
            )
        else:
            if self.year + 1 == self.current_year and self.month > self.current_month:
                month = self.current_month
            else:
                month = self.month
            keyboard.append(
                [
                    create_button(
                        f"{get_month_string(self.month, True, False )} {self.year - 1}   ◄",
                        str("month_previous_year"),
                        "month_previous_year",
                    ),
                    create_button(
                        f"{self.year}",
                        str("empty_button"),
                        "empty_button",
                    ),
                    create_button(
                        f"►   {get_month_string(month, True, False )} {self.year + 1}",
                        str("month_next_year"),
                        "month_next_year",
                    ),
                ]
            )
        return keyboard

    def retrieve_purchase(self, user: User) -> [Purchase]:
        """Retrieve of the purchases for the user

        Args:
            user (User): The user to query

        Returns:
            [Purchase]: The list of purchases
        """
        if not user_exists(user.id):
            create_user(user)
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
            footer = REPORT_PURCHASE_TOTAL % (spaces, footer)
            message = f"{message}\n\n{footer}"
        return message

    def previous_page(self, update: Update, context: CallbackContext):
        """Go to the previous page

        Args:
            update (Update): Telegram update
            context (CallbackContext): The context of the telegram bot
        """
        user = update.effective_user
        message_id = update.effective_message.message_id
        chat_id = update.effective_chat.id
        user_id = user.id
        if not is_owner(message_id, user_id):
            context.bot.answer_callback_query(
                update.callback_query.id, text=NOT_MESSAGE_OWNER, show_alert=True
            )
            return
        context.bot.answer_callback_query(update.callback_query.id)
        self.month -= 1
        message = self.retrieve_purchase(user)
        keyboard = self.build_keyboard()
        context.bot.edit_message_text(
            text=message,
            chat_id=chat_id,
            disable_web_page_preview=True,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
        )

    def next_page(self, update: Update, context: CallbackContext):
        """Go to the next page

        Args:
            update (Update): Telegram update
            context (CallbackContext): The context of the telegram bot
        """
        user = update.effective_user
        message_id = update.effective_message.message_id
        chat_id = update.effective_chat.id
        user_id = user.id
        if not is_owner(message_id, user_id):
            context.bot.answer_callback_query(
                update.callback_query.id, text=NOT_MESSAGE_OWNER, show_alert=True
            )
            return
        context.bot.answer_callback_query(update.callback_query.id)
        self.month += 1
        message = self.retrieve_purchase(user)
        keyboard = self.build_keyboard()
        context.bot.edit_message_text(
            text=message,
            chat_id=chat_id,
            disable_web_page_preview=True,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
        )

    def previous_year(self, update: Update, context: CallbackContext):
        """Go to the previous year

        Args:
            update (Update): Telegram update
            context (CallbackContext): The context of the telegram bot
        """
        user = update.effective_user
        message_id = update.effective_message.message_id
        chat_id = update.effective_chat.id
        user_id = user.id
        if not is_owner(message_id, user_id):
            context.bot.answer_callback_query(
                update.callback_query.id, text=NOT_MESSAGE_OWNER, show_alert=True
            )
            return
        context.bot.answer_callback_query(update.callback_query.id)
        self.year -= 1
        message = self.retrieve_purchase(user)
        keyboard = self.build_keyboard()
        context.bot.edit_message_text(
            text=message,
            chat_id=chat_id,
            disable_web_page_preview=True,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
        )

    def next_start_year(self, update: Update, context: CallbackContext):
        """Go to the next year but at the start

        Args:
            update (Update): Telegram update
            context (CallbackContext): The context of the telegram bot
        """
        user = update.effective_user
        message_id = update.effective_message.message_id
        chat_id = update.effective_chat.id
        user_id = user.id
        if not is_owner(message_id, user_id):
            context.bot.answer_callback_query(
                update.callback_query.id, text=NOT_MESSAGE_OWNER, show_alert=True
            )
            return
        context.bot.answer_callback_query(update.callback_query.id)
        self.year += 1
        self.month = 1
        if self.year == self.current_year:
            if self.month > self.current_month:
                self.month = self.current_month
        if self.year > self.current_year:
            self.year = self.current_year
        message = self.retrieve_purchase(user)
        keyboard = self.build_keyboard()
        context.bot.edit_message_text(
            text=message,
            chat_id=chat_id,
            disable_web_page_preview=True,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
        )

    def previous_start_year(self, update: Update, context: CallbackContext):
        """Go to the previous year but at the end

        Args:
            update (Update): Telegram update
            context (CallbackContext): The context of the telegram bot
        """
        user = update.effective_user
        message_id = update.effective_message.message_id
        chat_id = update.effective_chat.id
        user_id = user.id
        if not is_owner(message_id, user_id):
            context.bot.answer_callback_query(
                update.callback_query.id, text=NOT_MESSAGE_OWNER, show_alert=True
            )
            return
        context.bot.answer_callback_query(update.callback_query.id)
        self.year -= 1
        self.month = 12
        if self.year == self.current_year:
            if self.month > self.current_month:
                self.month = self.current_month
        if self.year > self.current_year:
            self.year = self.current_year
        message = self.retrieve_purchase(user)
        keyboard = self.build_keyboard()
        context.bot.edit_message_text(
            text=message,
            chat_id=chat_id,
            disable_web_page_preview=True,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
        )

    def next_year(self, update: Update, context: CallbackContext):
        """Go to the next year

        Args:
            update (Update): Telegram update
            context (CallbackContext): The context of the telegram bot
        """
        user = update.effective_user
        message_id = update.effective_message.message_id
        chat_id = update.effective_chat.id
        user_id = user.id
        if not is_owner(message_id, user_id):
            context.bot.answer_callback_query(
                update.callback_query.id, text=NOT_MESSAGE_OWNER, show_alert=True
            )
            return
        context.bot.answer_callback_query(update.callback_query.id)
        self.year += 1
        if self.year == self.current_year:
            if self.month > self.current_month:
                self.month = self.current_month
        if self.year > self.current_year:
            self.year = self.current_year
        message = self.retrieve_purchase(user)
        keyboard = self.build_keyboard()
        context.bot.edit_message_text(
            text=message,
            chat_id=chat_id,
            disable_web_page_preview=True,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
        )
