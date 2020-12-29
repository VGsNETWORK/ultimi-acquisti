#!/usr/bin/env python3

""" File containing functions to compare prices with other users """

import re
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
from root.util.telegram import TelegramSender

sender = TelegramSender()


def month_compare(update: Update, context: CallbackContext) -> None:
    """Compare the month with an user

    Args:
        update (Update): Telegram update
        context (CallbackContext): The context of the telegram bot
    """
    logger.info("received command month compare")
    compare(update, context, retrieve_sum_for_month, True)


def year_compare(update: Update, context: CallbackContext) -> None:
    """Compare the year with an user

    Args:
        update (Update): Telegram update
        context (CallbackContext): The context of the telegram bot
    """
    logger.info("received command year compare")
    compare(update, context, retrieve_sum_for_year, False)


def compare(
    update: Update, context: CallbackContext, function: callable, month: bool
) -> None:
    """General compare function used to compare month/year

    Args:
        update (Update): Telegram update
        context (CallbackContext): The context of the telegram bot
        function (callable): The function to call wich retrieves the sum
        month (bool): If you have to compare the month or the year
    """
    cdate = datetime.now()
    custom_year = cdate.year
    custom_month = cdate.month
    message: Message = update.message if update.message else update.edited_message
    user = message.from_user
    sender.delete_if_private(context, message)
    chat_id = message.chat.id
    if message.chat.type == "private":
        sender.send_and_delete(context, chat_id, ONLY_GROUP)
        return
    if not message.reply_to_message:
        sender.send_and_delete(context, chat_id, NO_QUOTE_FOUND)
        return
    rmessage: Message = message.reply_to_message
    arg_number = 2 if month else 1
    user_message = message.text if message.text else message.caption
    user_message = re.sub(r"/\w+\s", "", user_message)
    if len(user_message.split(" ")) > arg_number:
        # TODO: add example
        user_message = user_message.split(" ")[0].replace("/", "")
        error_message = TOO_MANY_ARGUMENTS % (user.id, user.first_name, user_message)
        sender.send_and_delete(context, chat_id=chat_id, text=error_message)
        return
    if not month:
        custom_year = message.text if message.text else message.caption
        custom_year = custom_year.split(" ")
        if len(custom_year) > 1:
            try:
                custom_year = int(custom_year[1])
            except Exception:
                # TODO: add example
                error_message = COMPARE_YEAR_NOT_VALID % (
                    user.id,
                    user.first_name,
                    custom_year[1],
                )
                sender.send_and_delete(
                    context=context, chat_id=chat_id, text=error_message
                )
                return
        else:
            custom_year = cdate.year
            custom_month = cdate.month
    else:
        custom_date = message.text if message.text else message.caption
        custom_date = re.sub(r"/\w+\s", "", custom_date)
        rdate = re.findall(r"(\w{1,9}\ \d{4})", custom_date)
        if rdate:
            rdate = rdate[0].split(" ")
            mtext = rdate[0]
            custom_year = int(rdate[1])
            if is_text_month(mtext):
                custom_month = get_month_number(mtext)
            else:
                # TODO: add example
                error_message = COMPARE_MONTH_NOT_VALID % (
                    user.id,
                    user.first_name,
                    mtext,
                )
                sender.send_and_delete(context, chat_id=chat_id, text=error_message)
                return
        if not rdate:
            rdate = re.findall(r"^\w{1,9}$", custom_date)
            if rdate:
                mtext = rdate[0]
                if is_text_month(mtext):
                    custom_month = get_month_number(mtext)
                    custom_year = cdate.year
                else:
                    # TODO: add example
                    error_message = COMPARE_MONTH_NOT_VALID % (
                        user.id,
                        user.first_name,
                        mtext,
                    )
                    sender.send_and_delete(context, chat_id=chat_id, text=error_message)
                    return
        if not rdate:
            custom_date = re.sub(r"/\w+", "", custom_date)
            if custom_date:
                try:
                    custom_date = custom_date.split("/")
                    custom_month = int(custom_date[0])
                    custom_year = int(custom_date[1])
                except Exception:
                    # TODO: add example
                    user_message = message.text if message.text else message.caption
                    user_message = user_message.split(" ")[0].replace("/", "")
                    error_message = COMMAND_FORMAT_ERROR % (
                        user.id,
                        user.first_name,
                        user_message,
                    )
                    sender.send_and_delete(context, chat_id=chat_id, text=error_message)
                    return
            else:
                custom_year = cdate.year
                custom_month = cdate.month
        else:
            custom_year = cdate.year
            custom_month = cdate.month
    if len(str(custom_year)) == 2:
        custom_year = int(f"20{custom_year}")
    if custom_year > cdate.year:
        error_message = message.text.split(" ")[0].replace("/", "")
        error_message = COMPARE_WRONG_YEAR % (
            user.id,
            user.first_name,
            error_message,
            custom_year,
        )
        sender.send_and_delete(context, chat_id, error_message)
        return
    if custom_year == cdate.year and custom_month > cdate.month:
        error_message = message.text.split(" ")[0].replace("/", "")
        error_message = COMPARE_WRONG_MONTH % (
            user.id,
            user.first_name,
            error_message,
            get_month_string(custom_month, False, True),
        )
        sender.send_and_delete(context, chat_id, error_message)
        return
    if not rmessage:
        return
    ruser = rmessage.from_user
    if not user_exists(user.id):
        create_user(user)
    if not user_exists(ruser.id):
        create_user(ruser)
    ruser_id = ruser.id
    user_id = user.id
    if ruser_id == user_id:
        sender.send_and_delete(context, chat_id, NO_QUOTE_YOURSELF)
        return
    if ruser.is_bot:
        sender.send_and_delete(context, chat_id, NO_QUOTE_BOT)
        return
    rfirst_name = ruser.first_name
    first_name = user.first_name
    if not month:
        upurchase = function(user_id, custom_year)
        rpurchase = function(ruser_id, custom_year)
        message = YEAR_COMPARE_PRICE % (
            custom_year,
            user_id,
            first_name,
            format_price(upurchase),
            rfirst_name,
            format_price(rpurchase),
        )
    else:
        upurchase = function(user_id, custom_month, custom_year)
        rpurchase = function(ruser_id, custom_month, custom_year)
        date = f"{get_month_string(custom_month, False, True)} {custom_year}"
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
        if int(rpurchase) != 0:
            message = f"{message}{COMPARE_TIE}"
        else:
            message = f"{message}{COMPARE_NO_PURCHASE}"
    sender.send_and_delete(context, chat_id, message)
