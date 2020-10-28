#!/usr/bin/env/python3

from telegram import Update, Message, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from root.contants.messages import (
    YEAR_USER_PURCHASES,
    YEAR_PURCHASES,
    YEAR_PREVIOUS_PURCHASES_HIGER,
    YEAR_PREVIOUS_PURCHASES_LOWER,
)
from root.helper.user_helper import create_user, user_exists
from root.helper.purchase_helper import (
    retrieve_sum_for_current_year,
    retrieve_sum_for_year,
)
from root.util.util import (
    get_current_month,
    get_current_year,
    is_group_allowed,
    format_price,
    create_button,
)
from root.util.telegram import TelegramSender

sender = TelegramSender()


def year_purchase(update: Update, context: CallbackContext) -> None:
    message: Message = update.message if update.message else update.edited_message
    expand = False if message.reply_to_message else True
    message = message.reply_to_message if message.reply_to_message else message
    sender.delete_if_private(update, context, message)
    chat_id = message.chat.id
    user = message.from_user
    user_id = user.id
    first_name = user.first_name
    chat_type = message.chat.type
    if not chat_type == "private":
        if not user_exists(user_id):
            create_user(user)
        if not is_group_allowed(chat_id):
            return
    price = retrieve_sum_for_current_year(user_id)
    keyboard = [
        [
            create_button(
                "Maggiori dettagli...", "expand_year_report", "expand_year_report"
            )
        ]
    ]
    if not message.reply_to_message:
        year = get_current_year() - 1
        pprice = retrieve_sum_for_year(user_id, year)
        diff = pprice - price if pprice > price else price - pprice
        diff = format_price(diff)
        append = (
            YEAR_PREVIOUS_PURCHASES_LOWER % (year, format_price(pprice), diff)
            if pprice > price
            else YEAR_PREVIOUS_PURCHASES_HIGER % (year, format_price(pprice), diff)
        )
        price = format_price(price)
        message = YEAR_PURCHASES % (
            user_id,
            first_name,
            get_current_year(),
            price,
        )
        message += append
    else:
        price = format_price(price)
        message = YEAR_USER_PURCHASES % (
            first_name,
            get_current_year(),
            price,
        )

    sender.send_and_delete(
        context,
        chat_id,
        message,
        reply_markup=InlineKeyboardMarkup(keyboard) if expand else None,
    )
