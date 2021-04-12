#!/usr/bin/env python3


""" File with class to show the year report """

from datetime import datetime
from functools import total_ordering
from root.contants.keyboard import NO_PURCHASE_KEYBOARD
from dateutil import tz
from telegram import InlineKeyboardMarkup, Message, Update, User
from telegram.ext import CallbackContext
from root.helper.user_helper import create_user, user_exists
from root.helper.redis_message import is_owner
from root.contants.messages import (
    NO_PURCHASE,
    YEAR_PURCHASE_REPORT,
    REPORT_PURCHASE_TOTAL,
    NO_YEAR_PURCHASE,
    YEAR_PURCHASE_TEMPLATE,
    NOT_MESSAGE_OWNER,
    SESSION_ENDED,
)
from root.model.purchase import Purchase
from root.helper.process_helper import create_process, restart_process
from root.helper.purchase_helper import (
    count_user_purchases_for_year,
    get_last_purchase,
    retrieve_month_purchases_for_user,
    retrieve_sum_for_month,
    retrieve_sum_for_year,
)
import root.util.logger as logger
from root.util.telegram import TelegramSender
from root.util.util import (
    append_timeout_message,
    format_price,
    get_month_string,
    is_group_allowed,
    is_number,
)
from root.helper.keyboard.year_report import build_keyboard
from root.contants.message_timeout import ONE_MINUTE, THREE_MINUTES
from root.manager.start import back_to_the_start
from root.helper.redis_message import add_message


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
        if expand:
            year = update.callback_query.data.split("_")[-1]
            self.year = int(year) if is_number(year) else self.year
        message: Message = update.effective_message
        if not message:
            message = update.callback_query.message
        if not update.callback_query:
            if not self.sender.check_command(message):
                return
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
        keyboard = build_keyboard(self.year, self.current_year)
        keyboard = InlineKeyboardMarkup(keyboard)
        message = self.retrieve_purchase(user)
        purchase = get_last_purchase(user.id)
        if not purchase:
            message = NO_PURCHASE % (user.id, user.first_name)
            keyboard = NO_PURCHASE_KEYBOARD
        is_private = not update.effective_chat.type == "private"
        if expand:
            try:
                if is_private or is_owner(message_id, user_id):
                    if not restart_process(message_id, THREE_MINUTES):
                        logger.info("Unable to restart process, recreating it")
                        create_process(
                            name_prefix=message_id,
                            target=back_to_the_start,
                            args=(update, context, chat_id, message_id, THREE_MINUTES),
                        )
                    context.bot.answer_callback_query(update.callback_query.id)
                    timeout = THREE_MINUTES if purchase else ONE_MINUTE
                    message = append_timeout_message(
                        message, is_private, timeout, is_private
                    )
                    context.bot.edit_message_text(
                        text=message,
                        chat_id=chat_id,
                        disable_web_page_preview=True,
                        message_id=message_id,
                        reply_markup=keyboard,
                        parse_mode="HTML",
                    )
                else:
                    context.bot.answer_callback_query(
                        update.callback_query.id,
                        text=NOT_MESSAGE_OWNER,
                        show_alert=True,
                    )
                return
            except ValueError as e:
                logger.exception(e)
                context.bot.answer_callback_query(
                    update.callback_query.id, text=SESSION_ENDED, show_alert=True
                )
                self.sender.delete_message(context, chat_id, message_id)
                return
        add_message(message_id, user_id)
        purchase = get_last_purchase(user.id)
        if not purchase:
            message = NO_PURCHASE % (user.id, user.first_name)
            keyboard = NO_PURCHASE_KEYBOARD
        timeout = THREE_MINUTES if purchase else ONE_MINUTE
        number_of_purchases = count_user_purchases_for_year(user_id, self.year)
        timeout = THREE_MINUTES if number_of_purchases else ONE_MINUTE
        logger.info(number_of_purchases)
        message = append_timeout_message(message, is_private, timeout, is_private)
        if update.effective_message.chat.type == "private":
            self.sender.send_and_edit(
                update,
                context,
                chat_id,
                message,
                back_to_the_start,
                keyboard,
                timeout=THREE_MINUTES,
            )
            return

        self.sender.send_and_delete(
            update.effective_message.message_id,
            update.effective_user.id,
            context,
            chat_id,
            message,
            reply_markup=keyboard,
            timeout=THREE_MINUTES,
        )

    def expand_report(self, update: Update, context: CallbackContext) -> None:
        """The callback to indicate to expand the year purchase message into the report

        Args:
            update (Update): Telegram update
            context (CallbackContext): The context of the telegram bot
        """
        self.year_report(update, context, True)

    def retrieve_purchase(self, user: User):
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
            retrieve_sum_for_month(user_id, i, self.year, True) for i in range(1, 13)
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
            price_check = [purchases[i] for i in range(0, mrange) if purchases[i] >= 0]
            if len(price_check) == 0:
                message = NO_YEAR_PURCHASE % (user_id, first_name, self.year)
            else:
                for i in range(0, mrange):
                    total_purchases = retrieve_month_purchases_for_user(
                        user_id, i + 1, self.year
                    )
                    total_purchases = len(total_purchases)
                    price = purchases[i]
                    if price >= 0:
                        price = format_price(price)
                        month = get_month_string(i + 1, False)
                        month = f"{month}"
                        if (
                            self.current_month == i + 1
                            and self.year == self.current_year
                        ):
                            month = f"► <i>{month}</i>"
                        spaces = " " * (spacer - len(price))
                        template = YEAR_PURCHASE_TEMPLATE % (
                            spaces,
                            price,
                            month,
                            total_purchases,
                            "o" if total_purchases == 1 else "i",
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
        query: str = update.callback_query.data
        year = query.split("_")[-1]
        self.year -= int(year)
        message = self.retrieve_purchase(user)
        keyboard = build_keyboard(self.year, self.current_year)
        keyboard = InlineKeyboardMarkup(keyboard)
        is_private = not update.effective_chat.type == "private"
        purchase = get_last_purchase(user.id)
        if not purchase:
            message = NO_PURCHASE % (user.id, user.first_name)
            keyboard = NO_PURCHASE_KEYBOARD
        timeout = THREE_MINUTES if purchase else ONE_MINUTE
        number_of_purchases = count_user_purchases_for_year(user_id, self.year)
        timeout = THREE_MINUTES if number_of_purchases else ONE_MINUTE
        logger.info(number_of_purchases)
        message = append_timeout_message(message, is_private, timeout, is_private)
        context.bot.edit_message_text(
            text=message,
            chat_id=chat_id,
            disable_web_page_preview=True,
            message_id=message_id,
            reply_markup=keyboard,
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
        query: str = update.callback_query.data
        year = query.split("_")[-1]
        self.year += int(year)
        if self.year >= self.current_year:
            self.year = self.current_year
        message = self.retrieve_purchase(user)
        keyboard = build_keyboard(self.year, self.current_year)
        keyboard = InlineKeyboardMarkup(keyboard)
        purchase = get_last_purchase(user.id)
        if not purchase:
            message = NO_PURCHASE % (user.id, user.first_name)
            keyboard = NO_PURCHASE_KEYBOARD
        timeout = THREE_MINUTES if purchase else ONE_MINUTE
        number_of_purchases = count_user_purchases_for_year(user_id, self.year)
        timeout = THREE_MINUTES if number_of_purchases else ONE_MINUTE
        logger.info(number_of_purchases)
        is_private = not update.effective_chat.type == "private"
        message = append_timeout_message(message, is_private, timeout, is_private)
        context.bot.edit_message_text(
            text=message,
            chat_id=chat_id,
            disable_web_page_preview=True,
            message_id=message_id,
            reply_markup=keyboard,
            parse_mode="HTML",
        )
