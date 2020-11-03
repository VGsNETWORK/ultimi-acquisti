#!/usr/bin/env python3

from telegram import Update, Message
from telegram.ext import CallbackContext
from root.contants.messages import (
    COMPARE_HE_WON, 
    COMPARE_NO_PURCHASE, 
    COMPARE_TIE, 
    COMPARE_YOU_WON, 
    YEAR_COMPARE_PRICE, 
    MONTH_COMPARE_PRICE
)
from root.helper.purchase_helper import (
    retrieve_sum_for_current_month, 
    retrieve_sum_for_current_year
)
from root.util.util import get_current_month, get_current_year



def month_compare(update: Update, context: CallbackContext):
    compare(update, context, MONTH_COMPARE_PRICE, True)

def year_compare(update: Update, context: CallbackContext):
    compare(update, context, YEAR_COMPARE_PRICE, False)

def compare(update: Update, context: CallbackContext, template: str, use_month: bool):
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
    if use_month:
        upurchase = retrieve_sum_for_current_month(user_id)
        rpurchase = retrieve_sum_for_current_month(ruser_id)
    else:
        upurchase = retrieve_sum_for_current_year(user_id)
        rpurchase = retrieve_sum_for_current_year(ruser_id)
    
    date = get_current_year()
    if use_month:
        date = f"{get_current_month(False, True)} {date}"

    message = template % (
        date,
        user_id,
        first_name,
        (f"%.2f" % upurchase).replace(".", ","),
        rfirst_name,
        (f"%.2f" % rpurchase).replace(".", ","),
    )
    if upurchase > rpurchase:
        diff = upurchase - rpurchase
        diff = (f"%.2f" % diff).replace(".", ",")
        message = f"{message}{COMPARE_YOU_WON % diff}"
    elif upurchase < rpurchase:
        diff = rpurchase - upurchase
        diff = (f"%.2f" % diff).replace(".", ",")
        message = f"{message}{COMPARE_HE_WON % diff}"
    else:
        if not int(rpurchase) == 0:
            message = f"{message}{COMPARE_TIE}"
        else:
            message = f"{message}{COMPARE_NO_PURCHASE}"
    context.bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")