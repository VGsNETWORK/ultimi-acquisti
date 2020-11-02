#!/usr/bin/env python3

""" File to retrieve the last purchase of the user """

from telegram import Update, Message
from telegram.ext import CallbackContext
from telegram.error import BadRequest
from root.util.logger import Logger
from root.util.util import is_group_allowed
from root.model.purchase import Purchase
from root.helper.purchase_helper import get_last_purchase
from root.helper.user_helper import user_exists, create_user
from root.contants.messages import (
    ONLY_GROUP,
    LAST_PURCHASE,
    NO_PURCHASE,
    NO_QUOTE_BOT,
    LAST_PURCHASE_USER,
)
from root.util.telegram import TelegramSender


sender = TelegramSender()
logger = Logger()


def last_purchase(update: Update, context: CallbackContext) -> None:
    """ Retrieve the last purchase of the user who typed the command """
    message: Message = update.message if update.message else update.edited_message
    sender.delete_if_private(context, message)
    chat_id = message.chat.id
    chat_type = message.chat.type
    user = update.effective_user
    user_id = user.id
    first_name = user.first_name
    if user.is_bot:
        sender.send_and_delete(context, chat_id, NO_QUOTE_BOT)
        return
    if not chat_type == "private":
        if not user_exists(user_id):
            create_user(user)
        if not is_group_allowed(chat_id):
            return
        purchase: Purchase = get_last_purchase(user_id)
    else:
        sender.send_and_delete(context, chat_id, ONLY_GROUP)
        return
    if message.reply_to_message:
        rmessage: Message = message.reply_to_message
        ruser = rmessage.from_user
        if ruser.is_bot:
            sender.send_and_delete(context, chat_id, NO_QUOTE_BOT)
            return
        user_id = ruser.id
        first_name = ruser.first_name
    purchase = get_last_purchase(user_id)
    if purchase:
        purchase_chat_id = str(purchase.chat_id).replace("-100", "")
        date = purchase.creation_date
        time = date.strftime("%H:%M")
        date = date.strftime("%d/%m/%Y")
        if not message.reply_to_message or user.id == user_id:
            message = LAST_PURCHASE % (
                user_id,
                first_name,
                date,
                time,
                purchase_chat_id,
                purchase.message_id,
            )
        else:
            message = LAST_PURCHASE_USER % (
                first_name,
                date,
                time,
                purchase_chat_id,
                purchase.message_id,
            )
        try:
            sender.send_and_delete(
                context, chat_id, message, reply_to_message_id=purchase.message_id
            )
        except BadRequest:
            sender.send_and_delete(context, chat_id, message)
    else:
        message = NO_PURCHASE % (user_id, first_name)
        sender.send_and_delete(context, chat_id, message)
