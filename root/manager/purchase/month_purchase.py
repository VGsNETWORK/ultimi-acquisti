#!/usr/bin/env/python3

""" File to show the sum of all the purchases in a month """

from telegram import Update, Message, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from root.contants.messages import (
    MONTH_USER_PURCHASES,
    MONTH_PURCHASES,
    MONTH_PREVIOUS_PURCHASES_HIGER,
    MONTH_PREVIOUS_PURCHASES_LOWER,
)
from root.helper.user_helper import create_user, user_exists
from root.helper.purchase_helper import (
    retrieve_sum_for_current_month,
    retrieve_sum_for_month,
)
from root.util.util import (
    get_current_month,
    get_current_year,
    is_group_allowed,
    format_price,
    create_button,
    get_month_string,
)
from root.util.telegram import TelegramSender

sender = TelegramSender()


def month_purchase(update: Update, context: CallbackContext) -> None:
    """send the sum of all purchases

    Args:
        update (Update): Telegram update
        context (CallbackContext): The context of the telegram bot
    """
    message: Message = update.message if update.message else update.edited_message
    expand = False if message.reply_to_message else True
    message = message.reply_to_message if message.reply_to_message else message
    chat_id = message.chat.id
    sender.delete_if_private(update, context, message)
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
    if not message.reply_to_message:
        month = get_current_month(number=True)
        year = get_current_year()
        year = year - 1 if month == 1 else year
        pprice = retrieve_sum_for_month(user_id, month - 1, year)
        diff = pprice - price if pprice > price else price - pprice
        diff = format_price(diff)
        mstring = (
            date
        ) = f"{get_month_string(month -1, False, True)} {get_current_year()}"
        append = (
            MONTH_PREVIOUS_PURCHASES_LOWER % (mstring, format_price(pprice), diff)
            if price > pprice
            else MONTH_PREVIOUS_PURCHASES_HIGER % (mstring, format_price(pprice), diff)
        )
        price = format_price(price)
        message = MONTH_PURCHASES % (
            user_id,
            first_name,
            get_current_month(False, True),
            price,
        )
        message += append
    else:
        price = format_price(price)
        date = f"{get_current_month( False, True)} {get_current_year()}"
        message = MONTH_USER_PURCHASES % (first_name, date, price)
    telegram_message: Message = (
        update.message if update.message else update.edited_message
    )
    chat_id = telegram_message.chat.id
    keyboard = [
        [create_button("Maggiori dettagli...", "expand_report", "expand_report")]
    ]
    sender.send_and_delete(
        context,
        chat_id,
        message,
        reply_markup=InlineKeyboardMarkup(keyboard) if expand else None,
    )
