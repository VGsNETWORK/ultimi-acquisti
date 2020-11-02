#!/usr/bin/env python3

""" File containing the function to delete a purchase """

from telegram import Update, Message
from telegram.ext import CallbackContext
from mongoengine.errors import DoesNotExist
from root.util.util import is_group_allowed
from root.helper.user_helper import create_user, user_exists
import root.helper.purchase_helper as purchase_helper
from root.contants.messages import CANCEL_PURCHASE_ERROR, PURCHASE_DELETED, ONLY_GROUP
from root.util.telegram import TelegramSender

sender = TelegramSender()


def delete_purchase(update: Update, context: CallbackContext) -> None:
    """delete a purchase from a user

    Args:
        update (Update): Telegram update
        context (CallbackContext): The context of the telegram bot
    """
    message: Message = update.message if update.message else update.edited_message
    sender.delete_if_private(context, message)
    chat_id = message.chat.id
    user = message.from_user
    if not user_exists(user.id):
        create_user(user)
    user_id = user.id
    first_name = user.first_name
    chat_type = message.chat.type
    if message.chat.type == "private":
        sender.send_and_delete(context, chat_id, ONLY_GROUP)
        return
    if not chat_type == "private":
        if not user_exists(user_id):
            create_user(user)
        if not is_group_allowed(chat_id):
            return
    message: Message = update.message if update.message else update.edited_message
    reply = message.reply_to_message
    user_id = update.effective_user.id
    chat_id = message.chat.id
    first_name = update.effective_user.first_name
    message_id = message.message_id
    if not reply:
        message = CANCEL_PURCHASE_ERROR % (user_id, first_name)
        sender.send_and_delete(context, chat_id, message)
        return
    try:
        message_id = reply.message_id
        purchase_helper.delete_purchase(user_id, message_id)
        context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        sender.send_and_delete(context, chat_id, PURCHASE_DELETED, timeout=10)
    except DoesNotExist:
        message_id = message.message_id
        message = CANCEL_PURCHASE_ERROR % (user_id, first_name)
        sender.send_and_delete(context, chat_id, message)
