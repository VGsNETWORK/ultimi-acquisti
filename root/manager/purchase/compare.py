#!/usr/bin/env python3

""" File containing functions to compare prices with other users """

import re
from html import escape
from datetime import datetime
from telegram import Update, Message
from telegram.ext import CallbackContext
from root.helper.user_helper import create_user, user_exists
from root.helper.purchase_helper import (
    retrieve_sum_for_month,
    retrieve_sum_for_year,
)
import root.util.logger as logger
from root.util.util import (
    format_price,
    get_month_string,
    is_text_month,
    get_month_number,
    month_starts_with,
)
from root.contants.messages import (
    MONTH_COMPARE_PRICE,
    COMPARE_HE_WON,
    COMPARE_NO_PURCHASE,
    COMPARE_TIE,
    COMPARE_YOU_WON,
    YEAR_COMPARE_PRICE,
    NO_QUOTE_YOURSELF,
    NO_QUOTE_BOT,
    ONLY_GROUP,
    NO_QUOTE_FOUND,
    COMPARE_WRONG_MONTH,
    COMPARE_WRONG_YEAR,
    COMPARE_MONTH_NOT_VALID,
    COMPARE_YEAR_NOT_VALID,
    TOO_MANY_ARGUMENTS,
    COMMAND_FORMAT_ERROR,
)
from root.contants.message_timeout import (
    SERVICE_TIMEOUT,
    ONE_MINUTE,
    TWO_MINUTES,
    LONG_SERVICE_TIMEOUT,
)
from root.util.telegram import TelegramSender

sender = TelegramSender()


def month_compare(update: Update, context: CallbackContext) -> None:
    """Compare the month with an user

    Args:
        update (Update): Telegram update
        context (CallbackContext): The context of the telegram bot
    """
    logger.info("received command month compare")
    compare(update, context, True)


def year_compare(update: Update, context: CallbackContext) -> None:
    """Compare the year with an user

    Args:
        update (Update): Telegram update
        context (CallbackContext): The context of the telegram bot
    """
    logger.info("received command year compare")
    compare(update, context, False)


def check_args(update: Update, context: CallbackContext, month: bool) -> bool:
    message: Message = update.message if update.message else update.edited_message
    user = message.from_user
    chat_id: int = message.chat.id
    argc: int = 2 if month else 1
    user_input: str = message.text if message.text else message.caption
    command = re.findall(r"/\S+", user_input)[0]
    args: str = re.sub(r"/\S+\s|/\S+", "", user_input)
    args: list(str) = args.split(" ")
    if len(args) > argc:
        command = create_command_append(command, month, True)
        error_message = TOO_MANY_ARGUMENTS % (user.id, user.first_name, command)
        sender.send_and_delete(
            update.effective_message.message_id,
            update.effective_user.id,
            context,
            chat_id=chat_id,
            text=error_message,
            timeout=LONG_SERVICE_TIMEOUT,
        )
        return False
    return True


def check_quote_and_users(update: Update, context: CallbackContext) -> bool:
    message: Message = update.message if update.message else update.edited_message
    user = message.from_user
    chat_id: int = message.chat.id
    rmessage: Message = message.reply_to_message
    if message.chat.type == "private":
        sender.send_and_delete(
            update.effective_message.message_id,
            update.effective_user.id,
            context,
            chat_id,
            ONLY_GROUP,
            timeout=SERVICE_TIMEOUT,
        )
        return False
    if not message.reply_to_message:
        sender.send_and_delete(
            update.effective_message.message_id,
            update.effective_user.id,
            context,
            chat_id,
            NO_QUOTE_FOUND,
            timeout=SERVICE_TIMEOUT,
        )
        return False
    reply_user = rmessage.from_user
    if not user_exists(user.id):
        create_user(user)
    if not user_exists(reply_user.id):
        create_user(reply_user)
    if reply_user.id == user.id:
        sender.send_and_delete(
            update.effective_message.message_id,
            update.effective_user.id,
            context,
            chat_id,
            NO_QUOTE_YOURSELF,
            timeout=SERVICE_TIMEOUT,
        )
        return False
    if reply_user.is_bot:
        sender.send_and_delete(
            update.effective_message.message_id,
            update.effective_user.id,
            context,
            chat_id,
            NO_QUOTE_BOT,
            timeout=SERVICE_TIMEOUT,
        )
        return False
    return True


def validate_month_and_send(update: Update, context: CallbackContext) -> bool:
    current_date = datetime.now()
    message: Message = update.message if update.message else update.edited_message
    reply_user = message.reply_to_message.from_user
    user = message.from_user
    first_name = user.first_name
    chat_id: int = message.chat.id
    user_input = message.text if message.text else message.caption

    command = re.findall(r"/\S+", user_input)[0]
    if "@" in command:
        command = re.findall(r"^.*?(?=@)", command)[0]
    args: str = re.sub(r"/\S+\s|/\S+", "", user_input)
    # Case when no arguments has been passed by the user
    if args:
        # Case where only one value has been passed (month string)
        month: str = re.findall(r"^\S{1,9}$", args)
        if month:
            month = month[0]
            if not is_text_month(month):
                example_month = month_starts_with(month)
                month = escape(month)
                command: str = create_command_append(command, True)
                message: str = COMPARE_MONTH_NOT_VALID % (
                    user.id,
                    first_name,
                    month,
                    command,
                    example_month[0],
                    example_month[1],
                )
                sender.send_and_delete(
                    update.effective_message.message_id,
                    update.effective_user.id,
                    context,
                    chat_id,
                    message,
                    timeout=TWO_MINUTES,
                )
                return False
            month: int = get_month_number(month)
            year = current_date.year
        else:
            # Case where two values has been passed
            user_date = re.findall(r"(^\S{1,9}\s\S{4}$)", args)
            if not user_date:
                user_input: list = user_input.split(" ")
                alternative: bool = len(user_input) > 2
                user_input: list = user_input[1:]
                if alternative:
                    user_input: str = f"{user_input[0]} {user_input[1]}"
                else:
                    user_input: str = f"{user_input[0][:15]}..."

                user_input = escape(user_input)
                command: str = create_command_append(command, True, alternative)
                message: str = COMMAND_FORMAT_ERROR % (
                    user.id,
                    first_name,
                    user_input,
                    command,
                )
                sender.send_and_delete(
                    update.effective_message.message_id,
                    update.effective_user.id,
                    context,
                    chat_id,
                    message,
                    timeout=ONE_MINUTE,
                )
                return False
            try:
                user_date = user_date[0]
                user_date = user_date.split(" ")
                month = user_date[0]
                if not is_text_month(month):
                    alternative: bool = len(user_input.split(" ")) > 2
                    example_month = month_starts_with(month)
                    command: str = create_command_append(command, True, alternative)
                    month = escape(month)
                    message: str = COMPARE_MONTH_NOT_VALID % (
                        user.id,
                        first_name,
                        month,
                        command,
                        example_month[0],
                        example_month[1],
                    )
                    sender.send_and_delete(
                        update.effective_message.message_id,
                        update.effective_user.id,
                        context,
                        chat_id,
                        message,
                        timeout=ONE_MINUTE,
                    )
                    return False
                month: int = get_month_number(month)
                year = int(user_date[1])
            except (ValueError, IndexError):
                user_input: list = user_input.split(" ")
                alternative: bool = len(user_input) > 2
                user_input: list = user_input[1:]
                if alternative:
                    user_input: str = f"{user_input[0]} {user_input[1]}"
                else:
                    user_input: str = f"{user_input[0][:15]}..."
                user_input = escape(user_input)
                command: str = create_command_append(command, True, alternative)
                message: str = COMMAND_FORMAT_ERROR % (
                    user.id,
                    first_name,
                    user_input,
                    command,
                )
                sender.send_and_delete(
                    update.effective_message.message_id,
                    update.effective_user.id,
                    context,
                    chat_id,
                    message,
                    timeout=ONE_MINUTE,
                )
                return False
    else:
        month = current_date.month
        year = current_date.year

    # check if the year is after the current one
    if year > current_date.year:
        command: str = create_command_append(command, True, True)
        message: str = COMPARE_WRONG_YEAR % (user.id, first_name, command, year)
        sender.send_and_delete(
            update.effective_message.message_id,
            update.effective_user.id,
            context,
            chat_id,
            message,
            timeout=ONE_MINUTE,
        )
        return False
    # check if the month is after the current one in this year
    if year == current_date.year:
        if month > current_date.month:
            alternative: bool = len(user_input.split(" ")) > 2
            command: str = create_command_append(command, True, alternative)
            message: str = COMPARE_WRONG_MONTH % (
                user.id,
                first_name,
                command,
                get_month_string(month, False, True),
            )
            sender.send_and_delete(
                update.effective_message.message_id,
                update.effective_user.id,
                context,
                chat_id,
                message,
                timeout=ONE_MINUTE,
            )
            return False
    user_purchase: float = retrieve_sum_for_month(user.id, month, year)
    reply_user_purchase: float = retrieve_sum_for_month(reply_user.id, month, year)
    message_date: str = f"{get_month_string(month, False, True)} {year}"
    message: str = MONTH_COMPARE_PRICE % (
        message_date,
        user.id,
        first_name,
        format_price(user_purchase),
        reply_user.first_name,
        format_price(reply_user_purchase),
    )
    message: str = get_compare_message(message, user_purchase, reply_user_purchase)
    sender.send_and_delete(
        update.effective_message.message_id,
        update.effective_user.id,
        context,
        chat_id,
        message,
        timeout=TWO_MINUTES,
    )
    return True


def validate_year_and_send(update: Update, context: CallbackContext):
    current_date = datetime.now()
    message: Message = update.message if update.message else update.edited_message
    reply_user = message.reply_to_message.from_user
    user = message.from_user
    first_name = user.first_name
    chat_id: int = message.chat.id
    user_input = message.text if message.text else message.caption

    command = re.findall(r"/\S+", user_input)[0]
    args: str = re.sub(r"/\S+\s|/\S+", "", user_input)
    if args:
        year = re.findall(r"^\S{4}$", args)
        if year:
            try:
                year = year[0]
                year = int(year)
            except (ValueError, IndexError):
                year = escape(year)
                command: str = create_command_append(command, False)
                message: str = COMPARE_YEAR_NOT_VALID % (
                    user.id,
                    first_name,
                    year,
                    command,
                )
                sender.send_and_delete(
                    update.effective_message.message_id,
                    update.effective_user.id,
                    context,
                    chat_id,
                    message,
                    timeout=ONE_MINUTE,
                )
                return False
        else:
            command: str = create_command_append(command, False)
            args = escape(args)
            message: str = COMPARE_YEAR_NOT_VALID % (
                user.id,
                first_name,
                args,
                command,
            )
            sender.send_and_delete(
                update.effective_message.message_id,
                update.effective_user.id,
                context,
                chat_id,
                message,
                timeout=ONE_MINUTE,
            )
            return False
    else:
        year = current_date.year

    # check if the year is after the current one
    if year > current_date.year:
        command: str = create_command_append(command, False)
        message: str = COMPARE_WRONG_YEAR % (user.id, first_name, command, year)
        sender.send_and_delete(
            update.effective_message.message_id,
            update.effective_user.id,
            context,
            chat_id,
            message,
            timeout=ONE_MINUTE,
        )
        return False

    user_purchase: float = retrieve_sum_for_year(user.id, year)
    reply_user_purchase: float = retrieve_sum_for_year(reply_user.id, year)
    message: str = YEAR_COMPARE_PRICE % (
        year,
        user.id,
        first_name,
        format_price(user_purchase),
        reply_user.first_name,
        format_price(reply_user_purchase),
    )
    message: str = get_compare_message(message, user_purchase, reply_user_purchase)
    sender.send_and_delete(
        update.effective_message.message_id,
        update.effective_user.id,
        context,
        chat_id,
        message,
        timeout=TWO_MINUTES,
    )
    return True


def get_compare_message(
    message: str, user_purchase: float, reply_user_purchase: float
) -> str:
    if user_purchase > reply_user_purchase:
        diff = user_purchase - reply_user_purchase
        diff = format_price(diff)
        return f"{message}{COMPARE_YOU_WON % diff}"
    if user_purchase < reply_user_purchase:
        diff = reply_user_purchase - user_purchase
        diff = format_price(diff)
        return f"{message}{COMPARE_HE_WON % diff}"
    if int(reply_user_purchase) != 0:
        return f"{message}{COMPARE_TIE}"
    return f"{message}{COMPARE_NO_PURCHASE}"


def create_command_append(command: str, month: bool, month_alternative: bool = False):
    if month_alternative:
        month_command: str = " &lt;mese&gt; &lt;anno&gt;"
    else:
        month_command: str = " &lt;mese&gt;"
    command += month_command if month else " &lt;anno&gt;"
    return command


def compare(update: Update, context: CallbackContext, month: bool):
    if not check_quote_and_users(update, context):
        return
    if not check_args(update, context, month):
        return

    if month:
        validate_month_and_send(update, context)
    else:
        validate_year_and_send(update, context)
