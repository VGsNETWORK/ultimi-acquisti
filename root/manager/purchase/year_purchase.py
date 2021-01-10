#!/usr/bin/env/python3

""" File to show the sum of all the purchases in a year """

from telegram import Update, Message, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from root.contants.messages import (
    YEAR_USER_PURCHASES,
    YEAR_PURCHASES,
    YEAR_PREVIOUS_PURCHASES_HIGHER,
    YEAR_PREVIOUS_PURCHASES_LOWER,
    YEAR_PREVIOUS_PURCHASE_NONE,
    YEAR_PURCHASES_NONE,
    YEAR_USER_PURCHASES_NONE,
    YEAR_PREVIOUS_PURCHASES_SAME,
    NO_QUOTE_BOT,
)
from root.helper.user_helper import create_user, user_exists
from root.helper.purchase_helper import (
    retrieve_sum_for_current_year,
    retrieve_sum_for_year,
)
from root.util.util import (
    get_current_year,
    is_group_allowed,
    format_price,
    create_button,
)
from root.util.telegram import TelegramSender
from root.contants.message_timeout import LONG_SERVICE_TIMEOUT
from root.manager.start import back_to_the_start
from root.helper.redis_message import add_message

sender = TelegramSender()


def year_purchase(update: Update, context: CallbackContext) -> None:
    """send the sum of all purchases

    Args:
        update (Update): Telegram update
        context (CallbackContext): The context of the telegram bot
    """
    message: Message = update.message if update.message else update.edited_message
    expand = not message.reply_to_message
    message = message.reply_to_message if message.reply_to_message else message
    sender.delete_if_private(context, message)
    message_id = message.message_id
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
    if user.is_bot:
        message: str = NO_QUOTE_BOT % (user_id, user.first_name)
        sender.send_and_delete(
            update.effective_message.message_id,
            update.effective_user.id,
            context,
            chat_id,
            message,
        )
        return
    self_quote = update.effective_user.id == user_id
    if expand or self_quote:
        year = get_current_year() - 1
        pprice = retrieve_sum_for_year(user_id, year)
        diff = pprice - price if pprice > price else price - pprice
        diff = format_price(diff)
        append = (
            YEAR_PREVIOUS_PURCHASES_LOWER % (year, format_price(pprice), diff)
            if price > pprice
            else YEAR_PREVIOUS_PURCHASES_HIGHER % (year, format_price(pprice), diff)
        )
        if pprice == price:
            append = YEAR_PREVIOUS_PURCHASES_SAME % (year, format_price(pprice))
        if pprice == 0:
            append = YEAR_PREVIOUS_PURCHASE_NONE % year
        if price == 0:
            message = YEAR_PURCHASES_NONE % (
                user_id,
                first_name,
                get_current_year(),
            )
            append = f"📉{append[1:]}"
        if pprice == price == 0:
            message = YEAR_PURCHASES_NONE % (
                user_id,
                first_name,
                get_current_year(),
            )
            append = f"➖{append[1:]}"
        else:
            price = format_price(price)
            message = YEAR_PURCHASES % (
                user_id,
                first_name,
                get_current_year(),
                price,
            )
        message += append
    else:
        if price == 0:
            message = YEAR_USER_PURCHASES_NONE % (first_name, get_current_year())
        else:
            price = format_price(price)
            message = YEAR_USER_PURCHASES % (
                first_name,
                get_current_year(),
                price,
            )
    add_message(message_id, user_id)
    if update.effective_message.chat.type == "private":
        sender.send_and_edit(
            update,
            context,
            chat_id,
            message,
            back_to_the_start,
            InlineKeyboardMarkup(keyboard),
            timeout=LONG_SERVICE_TIMEOUT,
        )
        return

    sender.send_and_delete(
        update.effective_message.message_id,
        update.effective_user.id,
        context,
        chat_id,
        message,
        reply_markup=InlineKeyboardMarkup(keyboard) if expand or self_quote else None,
        timeout=LONG_SERVICE_TIMEOUT,
    )
