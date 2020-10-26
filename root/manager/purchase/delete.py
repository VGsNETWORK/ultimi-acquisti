#!/usr/bin/env python3

from telegram import Update, Message
from telegram.ext import CallbackContext
from root.util.util import is_group_allowed
from mongoengine.errors import DoesNotExist
import root.helper.purchase_helper as purchase_helper
from root.helper.user_helper import user_exists, create_user
from root.contants.messages import CANCEL_PURCHASE_ERROR, PURCHASE_DELETED
from root.util.telegram import TelegramSender

sender = TelegramSender()


def delete_purchase(update: Update, context: CallbackContext):
    message: Message = update.message if update.message else update.edited_message
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
        sender.send_and_delete(context, chat_id, PURCHASE_DELETED)
    except DoesNotExist:
        message_id = message.message_id
        message = CANCEL_PURCHASE_ERROR % (user_id, first_name)
        sender.send_and_delete(context, chat_id, message)