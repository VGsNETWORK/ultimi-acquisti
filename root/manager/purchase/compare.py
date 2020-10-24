#!/usr/bin/env python3

from telegram import Update, Message
from telegram.ext import CallbackContext
from root.helper.purchase_helper import (
    retrieve_sum_for_current_month,
    retrieve_sum_for_current_year,
)
from root.util.logger import Logger
from root.util.util import get_current_year, get_current_month, format_price
from root.contants.messages import (
    MONTH_COMPARE_PRICE,
    COMPARE_HE_WON,
    COMPARE_NO_PURCHASE,
    COMPARE_TIE,
    COMPARE_YOU_WON,
    YEAR_COMPARE_PRICE,
)

logger = Logger()


def month_compare(update: Update, context: CallbackContext):
    compare(update, context, retrieve_sum_for_current_month, True)


def year_compare(update: Update, context: CallbackContext):
    compare(update, context, retrieve_sum_for_current_year, False)


def compare(update: Update, context: CallbackContext, function: callable, month: bool):
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
    upurchase = function(user_id)
    rpurchase = function(ruser_id)
    if not month:
        message = YEAR_COMPARE_PRICE % (
            get_current_year(),
            user_id,
            first_name,
            format_price(upurchase),
            rfirst_name,
            format_price(rpurchase),
        )
    else:
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