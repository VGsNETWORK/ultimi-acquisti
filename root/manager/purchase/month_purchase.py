#!/usr/bin/env/python3

""" File to show the sum of all the purchases in a month """

from root.contants.keyboard import NO_PURCHASE_KEYBOARD
from telegram import Update, Message, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from root.contants.messages import (
    MONTH_USER_PURCHASES,
    MONTH_PURCHASES,
    MONTH_PREVIOUS_PURCHASES_HIGHER,
    MONTH_PREVIOUS_PURCHASES_LOWER,
    MONTH_PREVIOUS_PURCHASES_NONE,
    MONTH_PURCHASES_NONE,
    MONTH_USER_PURCHASES_NONE,
    MONTH_PREVIOUS_PURCHASES_SAME, NO_PURCHASE,
    NO_QUOTE_BOT,
)
from root.helper.user_helper import create_user, user_exists
from root.helper.purchase_helper import (
    get_last_purchase, retrieve_sum_for_current_month,
    retrieve_sum_for_month,
)
from root.util.util import (
    append_timeout_message, get_current_month,
    get_current_year,
    is_group_allowed,
    format_price,
    create_button,
    get_month_string,
)
from root.util.telegram import TelegramSender
from root.contants.message_timeout import LONG_SERVICE_TIMEOUT, SERVICE_TIMEOUT
from root.manager.start import back_to_the_start
from root.helper.redis_message import add_message

sender = TelegramSender()


def month_purchase(update: Update, context: CallbackContext) -> None:
    """send the sum of all purchases

    Args:
        update (Update): Telegram update
        context (CallbackContext): The context of the telegram bot
    """
    message: Message = update.message if update.message else update.edited_message
    if not sender.check_command(message):
        return
    expand = not message.reply_to_message
    message = message.reply_to_message if message.reply_to_message else message
    chat_id = message.chat.id
    sender.delete_if_private(context, message)
    chat_type = message.chat.type
    message_id = message.message_id
    user = message.from_user
    user_id = user.id
    first_name = user.first_name
    if not chat_type == "private":
        if not user_exists(user_id):
            create_user(user)
        if not is_group_allowed(chat_id):
            return
    price = retrieve_sum_for_current_month(user_id)
    self_quote = update.effective_user.id == user_id
    if user.is_bot:
        message: str = NO_QUOTE_BOT % (user_id, user.first_name)
        sender.send_and_delete(
            update.effective_message.message_id,
            update.effective_user.id,
            context,
            chat_id,
            message,
            timeout=SERVICE_TIMEOUT,
        )
        return
    if expand or self_quote:
        month = get_current_month(number=True)
        year = get_current_year()
        year = year - 1 if month == 1 else year
        pprice = retrieve_sum_for_month(user_id, month - 1, year)
        diff = pprice - price if pprice > price else price - pprice
        diff = format_price(diff)
        current_year: int = get_current_year()
        current_year: int = current_year - 1 if month == 1 else current_year
        mstring = date = f"{get_month_string(month - 1, False, True)} {current_year}"
        append = (
            MONTH_PREVIOUS_PURCHASES_LOWER % (mstring, format_price(pprice), diff)
            if price > pprice
            else MONTH_PREVIOUS_PURCHASES_HIGHER % (mstring, format_price(pprice), diff)
        )
        if pprice == price:
            append = MONTH_PREVIOUS_PURCHASES_SAME % (mstring, format_price(pprice))
        if pprice == 0:
            append = MONTH_PREVIOUS_PURCHASES_NONE % mstring
        if price == 0:
            message = MONTH_PURCHASES_NONE % (
                user_id,
                first_name,
                get_current_month(False, True),
            )
            append = f"📉{append[1:]}"
        if pprice == price == 0:
            message = MONTH_PURCHASES_NONE % (
                user_id,
                first_name,
                get_current_month(False, True),
            )
            append = f"➖{append[1:]}"
        else:
            price = format_price(price)
            message = MONTH_PURCHASES % (
                user_id,
                first_name,
                get_current_month(False, True),
                price,
            )
        message += append
    else:
        date = f"{get_current_month( False, True)} {get_current_year()}"
        if price == 0:
            message = MONTH_USER_PURCHASES_NONE % (first_name, date)
        else:
            price = format_price(price)
            message = MONTH_USER_PURCHASES % (first_name, date, price)
    telegram_message: Message = (
        update.message if update.message else update.edited_message
    )
    chat_id = telegram_message.chat.id
    keyboard = [
        [create_button("Maggiori dettagli...", "expand_report", "expand_report")]
    ]
    keyboard = InlineKeyboardMarkup(keyboard)
    add_message(message_id, user_id)
    purchase = get_last_purchase(user.id)
    is_private = not update.effective_chat.type == "private"
    if not purchase:
        expand = True
        message = NO_PURCHASE % (user.id, user.first_name)
        keyboard = NO_PURCHASE_KEYBOARD
    message = append_timeout_message(message, is_private, LONG_SERVICE_TIMEOUT, is_private)
    if update.effective_message.chat.type == "private":
        sender.send_and_edit(
            update,
            context,
            chat_id,
            message,
            back_to_the_start,
            keyboard,
            timeout=LONG_SERVICE_TIMEOUT,
        )
        return

    sender.send_and_delete(
        update.effective_message.message_id,
        update.effective_user.id,
        context,
        chat_id,
        message,
        reply_markup=keyboard if expand or self_quote else None,
        timeout=LONG_SERVICE_TIMEOUT,
    )
