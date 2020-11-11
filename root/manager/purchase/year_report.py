#!/usr/bin/env python3


""" File with class to show the year report """

from datetime import datetime
from dateutil import tz
from telegram import InlineKeyboardMarkup, Message, Update, User, InlineKeyboardButton
from telegram.ext import CallbackContext
from root.helper.user_helper import create_user, user_exists
from root.helper.redis_message import add_message, is_owner
from root.contants.messages import (
    YEAR_PURCHASE_REPORT,
    REPORT_PURCHASE_TOTAL,
    NO_YEAR_PURCHASE,
    YEAR_PURCHASE_TEMPLATE,
    NOT_MESSAGE_OWNER,
    SESSION_ENDED,
)
from root.model.purchase import Purchase
from root.helper.process_helper import restart_process
from root.helper.purchase_helper import retrieve_sum_for_month, retrieve_sum_for_year
import root.util.logger as logger
from root.util.telegram import TelegramSender
from root.util.util import (
    create_button,
    format_price,
    get_month_string,
    is_group_allowed,
)


class YearReport:
    """ Class used to display the year report of a user """

    def __init__(self):
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
        """Show the year report of a user

        Args:
            update (Update): Telegram update
            context (CallbackContext): The context of the telegram bot
            expand (bool, optional): if the call comes from a purchase message. Defaults to False.
        """
        logger.info("Received year report command")
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
            try:
                if is_owner(message_id, user_id):
                    restart_process(message_id)
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
                        update.callback_query.id,
                        text=NOT_MESSAGE_OWNER,
                        show_alert=True,
                    )
                return
            except ValueError:
                context.bot.answer_callback_query(
                    update.callback_query.id, text=SESSION_ENDED, show_alert=True
                )
                self.sender.delete_message(context, chat_id, message_id)
                return
        add_message(message_id, user_id)
        self.sender.send_and_delete(
            context,
            chat_id,
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            timeout=180,
        )

    def expand_report(self, update: Update, context: CallbackContext) -> None:
        """The callback to indicate to expand the year purchase message into the report

        Args:
            update (Update): Telegram update
            context (CallbackContext): The context of the telegram bot
        """
        self.year_report(update, context, True)

    def build_keyboard(self) -> [[InlineKeyboardButton]]:
        """Create the keyboard for the report

        Returns:
            [[InlineKeyboardButton]]: Array of Arrays of Keyboard Buttons
        """
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

    def retrieve_purchase(self, user: User) -> [Purchase]:
        """Retrieve of the purchases for the user

        Args:
            user (User): The user to query

        Returns:
            [Purchase]: The list of purchases
        """
        if not user_exists(user.id):
            create_user(user)
        user_id = user.id
        first_name = user.first_name
        purchases = [
            retrieve_sum_for_month(user_id, i, self.year) for i in range(1, 13)
        ]
        if not purchases:
            message = NO_YEAR_PURCHASE % (user_id, first_name, self.year)
        else:
            message = YEAR_PURCHASE_REPORT % (user_id, first_name, self.year)
            mrange = self.current_month if self.year == self.current_year else 12
            spacer = [len(format_price(price)) for price in purchases]
            footer = retrieve_sum_for_year(user_id, self.year)
            footer = format_price(footer)
            spacer.append(len(footer))
            spacer.sort()
            spacer = spacer[-1]
            for i in range(0, mrange):
                price = format_price(purchases[i])
                month = get_month_string(i + 1, False)
                spaces = " " * (spacer - len(price))
                template = YEAR_PURCHASE_TEMPLATE % (
                    spaces,
                    price,
                    month,
                )
                message = f"{message}\n{template}"
            spaces = " " * (spacer - len(footer))
            footer = REPORT_PURCHASE_TOTAL % (spaces, footer)
            line = "—" * (spacer + 2)
            message = f"{message}\n<code>{line}</code>"
            message = f"{message}\n{footer}"
        return message

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
        try:
            if not is_owner(message_id, user_id):
                context.bot.answer_callback_query(
                    update.callback_query.id, text=NOT_MESSAGE_OWNER, show_alert=True
                )
                return
        except ValueError:
            context.bot.answer_callback_query(
                update.callback_query.id, text=SESSION_ENDED, show_alert=True
            )
            self.sender.delete_message(context, chat_id, message_id)
            return
        restart_process(message_id)
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
        try:
            if not is_owner(message_id, user_id):
                context.bot.answer_callback_query(
                    update.callback_query.id, text=NOT_MESSAGE_OWNER, show_alert=True
                )
                return
        except ValueError:
            context.bot.answer_callback_query(
                update.callback_query.id, text=SESSION_ENDED, show_alert=True
            )
            self.sender.delete_message(context, chat_id, message_id)
            return
        restart_process(message_id)
        context.bot.answer_callback_query(update.callback_query.id)
        self.year += 1
        if self.year >= self.current_year:
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
