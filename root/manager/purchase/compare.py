#!/usr/bin/env python3

from telegram import Update, Message
from telegram.ext import CallbackContext
from datetime import datetime
from root.helper.purchase_helper import (
    retrieve_sum_for_current_month,
    retrieve_sum_for_current_year,
    retrieve_sum_for_month,
    retrieve_sum_for_year,
)
from root.util.logger import Logger
from root.util.util import (
    get_current_year,
    get_current_month,
    format_price,
    get_month_string,
)
from root.contants.messages import (
    MONTH_COMPARE_PRICE,
    COMPARE_HE_WON,
    COMPARE_NO_PURCHASE,
    COMPARE_TIE,
    COMPARE_YOU_WON,
    YEAR_COMPARE_PRICE,
    COMPARE_YOURSELF,
    COMPARE_BOT,
)
from root.util.telegram import TelegramSender

sender = TelegramSender()

logger = Logger()


def month_compare(update: Update, context: CallbackContext):
    compare(update, context, retrieve_sum_for_month, True)


def year_compare(update: Update, context: CallbackContext):
    compare(update, context, retrieve_sum_for_year, False)


def compare(update: Update, context: CallbackContext, function: callable, month: bool):
    cdate = datetime.now()
    custom_year = cdate.year
    custom_month = cdate.month
    message: Message = update.message if update.message else update.edited_message
    rmessage: Message = message.reply_to_message
    if not month:
        custom_year = message.text if message.text else message.caption
        custom_year = custom_year.split(" ")
        if len(custom_year) > 1:
            try:
                custom_year = int(custom_year[1])
            except ValueError:
                custom_year = cdate.year
    else:
        custom_date = message.text if message.text else message.caption
        custom_date = custom_date.split(" ")
        if len(custom_date) > 1:
            try:
                custom_date = custom_date[1]
                custom_date = custom_date.split("/")
                custom_month = int(custom_date[0])
                custom_year = int(custom_date[1])
            except Exception as e:
                custom_year = cdate.year
                custom_month = cdate.month
    if not rmessage:
        return
    chat_id = message.chat.id
    ruser = rmessage.from_user
    user = message.from_user
    ruser_id = ruser.id
    user_id = user.id
    if ruser_id == user_id:
        sender.send_and_delete(context, chat_id, COMPARE_YOURSELF)
        return
    if ruser.is_bot:
        sender.send_and_delete(context, chat_id, COMPARE_BOT)
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
        logger.info(f"{custom_year}, {custom_month}")
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
        if not int(rpurchase) == 0:
            message = f"{message}{COMPARE_TIE}"
        else:
            message = f"{message}{COMPARE_NO_PURCHASE}"
    sender.send_and_delete(context, chat_id, message)