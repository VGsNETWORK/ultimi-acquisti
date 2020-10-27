#!/usr/bin/env/python3

from telegram import Update, Message, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from root.contants.messages import MONTH_USER_PURCHASES, MONTH_PURCHASES
from root.helper.user_helper import create_user, user_exists
from root.helper.purchase_helper import retrieve_sum_for_current_month
from root.util.util import (
    get_current_month,
    get_current_year,
    is_group_allowed,
    format_price,
    create_button,
)
from root.util.telegram import TelegramSender

sender = TelegramSender()


def month_purchase(update: Update, context: CallbackContext) -> None:
    message: Message = update.message if update.message else update.edited_message
    expand = False if message.reply_to_message else True
    message = message.reply_to_message if message.reply_to_message else message
    chat_id = message.chat.id
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
    date = f"{get_current_month( False, True)} {get_current_year()}"
    price = format_price(price)
    if not message.reply_to_message:
        message = MONTH_PURCHASES % (user_id, first_name, date, price)
    else:
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