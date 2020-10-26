#!/usr/bin/env/python3

from telegram import Update, Message, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from root.contants.messages import YEAR_USER_PURCHASES, YEAR_PURCHASES
from root.helper.user_helper import create_user, user_exists
from root.helper.purchase_helper import retrieve_sum_for_current_year
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
    template: str = YEAR_USER_PURCHASES if message.reply_to_message else YEAR_PURCHASES
    expand = False if message.reply_to_message else True
    message = message.reply_to_message if message.reply_to_message else message
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
    price = format_price(price)
    keyboard = [
        [
            create_button(
                "Maggiori dettagli...", "expand_year_report", "expand_year_report"
            )
        ]
    ]
    message = template % (
        user_id,
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
