#!/usr/bin/env python3

""" File with class to show the month report """

from datetime import datetime
from dateutil import tz
from telegram import InlineKeyboardMarkup, Message, Update, User
from telegram.ext import CallbackContext
from root.helper.redis_message import add_message, is_owner
from root.model.purchase import Purchase
from root.contants.messages import (
    MONTH_PURCHASE_REPORT,
    REPORT_PURCHASE_TOTAL,
    NO_MONTH_PURCHASE,
    PURCHASE_REPORT_TEMPLATE,
    NOT_MESSAGE_OWNER,
    SESSION_ENDED,
)
from root.helper.purchase_helper import (
    retrieve_month_purchases_for_user,
    retrieve_sum_for_month,
)
from root.helper.process_helper import restart_process
from root.helper.user_helper import create_user, user_exists
import root.util.logger as logger
from root.util.telegram import TelegramSender
from root.util.util import (
    format_price,
    get_month_string,
    is_group_allowed,
    is_number,
)
from root.helper.keyboard.month_report import build_keyboard
from root.helper.report import check_owner
from root.contants.message_timeout import FIVE_MINUTES


class MonthReport:
    """ Class used to display the month report of a user """

    def __init__(self):
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
        logger.info("received month report command")
        current_date = datetime.now()
        self.month = current_date.month
        self.current_month = current_date.month
        self.year = current_date.year
        self.current_year = current_date.year
        if expand:
            query: str = update.callback_query.data
            year = query.split("_")[-1]
            if is_number(year):
                self.year = int(year)
                self.month = 1
                if "current" in query:
                    self.month = self.current_month
        message: Message = update.message if update.message else update.edited_message
        if not message:
            message = update.effective_message
        else:
            if not expand:
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
        keyboard = build_keyboard(
            self.month, self.current_month, self.year, self.current_year
        )
        message = self.retrieve_purchase(user)
        if expand:
            try:
                if is_owner(message_id, user_id):
                    restart_process(message_id, FIVE_MINUTES)
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
            InlineKeyboardMarkup(keyboard),
            timeout=FIVE_MINUTES,
        )

    def expand_report(self, update: Update, context: CallbackContext) -> None:
        """The callback to indicate to expand the month purchase message into the report

        Args:
            update (Update): Telegram update
            context (CallbackContext): The context of the telegram bot
        """
        self.month_report(update, context, True)

    # =========================================================================
    def retrieve_purchase(self, user: User) -> [Purchase]:
        """Retrieve of the purchases for the user

        Args:
            user (User): The user to query

        Returns:
            [Purchase]: The list of purchases
        """
        if self.month > 12:
            self.month = 1
            self.year += 1
        if self.month < 1:
            self.year -= 1
            self.month = 12
        user_id = user.id
        first_name = user.first_name
        purchases = retrieve_month_purchases_for_user(user_id, self.month, self.year)
        date = f"{get_month_string(self.month, False, True)} {self.year}"
        if not purchases:
            message = NO_MONTH_PURCHASE % (user_id, first_name, date)
        else:
            message = MONTH_PURCHASE_REPORT % (user_id, first_name, date)

            spacer = [len(format_price(purchase.price)) for purchase in purchases]
            footer = retrieve_sum_for_month(user_id, self.month, self.year)
            footer = format_price(footer)
            spacer.append(len(footer))
            spacer.sort()
            spacer = spacer[-1]

            for purchase in purchases:
                price = format_price(purchase.price)
                creation_date = purchase.creation_date
                creation_date = creation_date.strftime(
                    f"%d {get_month_string(creation_date.month)}, %H:%M"
                )
                if purchase.description:
                    creation_date = purchase.description
                    creation_date = (
                        f"{creation_date[:20]}..."
                        if len(creation_date) > 20
                        else creation_date
                    )
                spaces = " " * (spacer - len(price))
                template = PURCHASE_REPORT_TEMPLATE % (
                    spaces,
                    price,
                    str(purchase.chat_id).replace("-100", ""),
                    purchase.message_id,
                    creation_date,
                )
                message = f"{message}\n{template}"
            line = "—" * (spacer + 2)
            message = f"{message}\n<code>{line}</code>"
            spaces = " " * (spacer - len(footer))
            footer = REPORT_PURCHASE_TOTAL % (spaces, footer)
            message = f"{message}\n{footer}"
        return message

    # =========================================================================
    def previous_page(self, update: Update, context: CallbackContext):
        """Go to the previous page

        Args:
            update (Update): Telegram update
            context (CallbackContext): The context of the telegram bot
        """
        if not check_owner(update, context):
            return
        self.month -= 1
        self.retrieve_and_send(update, context)

    def next_page(self, update: Update, context: CallbackContext):
        """Go to the next page

        Args:
            update (Update): Telegram update
            context (CallbackContext): The context of the telegram bot
        """
        if not check_owner(update, context):
            return
        self.month += 1
        self.retrieve_and_send(update, context)

    def current_month_report(self, update: Update, context: CallbackContext):
        """Go to the beginning of the year

        Args:
            update (Update): Telegram update
            context (CallbackContext): The context of the telegram bot
        """
        if not check_owner(update, context):
            return
        self.month = 1
        self.retrieve_and_send(update, context)

    def previous_year(self, update: Update, context: CallbackContext):
        """Go to the previous year

        Args:
            update (Update): Telegram update
            context (CallbackContext): The context of the telegram bot
        """
        if not check_owner(update, context):
            return
        query: str = update.callback_query.data
        year = query.split("_")[-1]
        self.year = self.year - int(year)
        self.retrieve_and_send(update, context)

    def next_year(self, update: Update, context: CallbackContext):
        """Go to the next year

        Args:
            update (Update): Telegram update
            context (CallbackContext): The context of the telegram bot
        """
        if not check_owner(update, context):
            return
        query: str = update.callback_query.data
        year = query.split("_")[-1]
        self.year = self.year + int(year)
        if self.year == self.current_year:
            if self.month > self.current_month:
                self.month = self.current_month
        self.retrieve_and_send(update, context)

    def retrieve_and_send(self, update: Update, context: CallbackContext):
        """[summary]

        Args:
            update (Update): Telegram update
            context (CallbackContext): The context of the telegram bot
        """
        user = update.effective_user
        if not user_exists(user.id):
            create_user(user)
        message_id = update.effective_message.message_id
        chat_id = update.effective_chat.id
        message = self.retrieve_purchase(user)
        keyboard = build_keyboard(
            self.month, self.current_month, self.year, self.current_year
        )
        context.bot.edit_message_text(
            text=message,
            chat_id=chat_id,
            disable_web_page_preview=True,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
        )
