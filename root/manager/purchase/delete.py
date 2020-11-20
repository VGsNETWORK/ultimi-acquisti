#!/usr/bin/env python3

""" File containing the function to delete a purchase """

from telegram import Update, Message, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from mongoengine.errors import DoesNotExist
from pyrogram.types import Message as PyroMessage
from pyrogram import Client
from root.util.util import is_group_allowed
from root.helper.user_helper import create_user, user_exists
import root.helper.purchase_helper as purchase_helper
from root.contants.messages import (
    CANCEL_PURCHASE_ERROR,
    PURCHASE_DELETED,
    ONLY_GROUP,
    PURCHASE_NOT_FOUND,
    NOT_YOUR_PURCHASE,
    NO_QUOTE_BOT,
    NOT_A_PURCHASE,
)
from root.util.telegram import TelegramSender
from root.contants.message_timeout import SERVICE_TIMEOUT, LONG_SERVICE_TIMEOUT
from root.util.util import create_button, retrieve_key

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
        sender.send_and_delete(context, chat_id, ONLY_GROUP, timeout=SERVICE_TIMEOUT)
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
        sender.send_and_delete(context, chat_id, message, timeout=SERVICE_TIMEOUT)
        return
    if reply.from_user.is_bot:
        sender.send_and_delete(context, chat_id, NO_QUOTE_BOT, timeout=SERVICE_TIMEOUT)
        return
    if not "#ultimiacquisti" in reply.text:
        message = NOT_A_PURCHASE % (user_id, first_name)
        bot_name = retrieve_key("BOT_NAME")
        keyboard = [
            [
                create_button(
                    "Scopri di più",
                    callback="help_redirect",
                    query="help_redirect",
                    url=f"t.me/{bot_name}?start=how_to",
                )
            ]
        ]
        sender.send_and_delete(
            context,
            chat_id,
            message,
            timeout=LONG_SERVICE_TIMEOUT,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return
    try:
        message_id = reply.message_id
        purchase = purchase_helper.find_by_message_id(message_id)
        if purchase.user_id == user_id:
            purchase_helper.delete_purchase(user_id, message_id)
            context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            message = PURCHASE_DELETED
        else:
            message = NOT_YOUR_PURCHASE % (user_id, first_name)
        sender.send_and_delete(context, chat_id, message, timeout=SERVICE_TIMEOUT)
    except DoesNotExist:
        message_id = message.message_id
        message = PURCHASE_NOT_FOUND % (user_id, first_name)
        sender.send_and_delete(context, chat_id, message, timeout=SERVICE_TIMEOUT)


def remove_purchase(client: Client, message: PyroMessage) -> None:
    """Remove a purchase after the #ultimiacquisti has been removed

    Args:
        client (Client): The mtproto client
        message (PyroMessage): The mtproto Message
    """
    message_id: int = message.message_id
    user_id: int = message.from_user.id
    chat_id = message.chat.id
    purchase_helper.delete_purchase(user_id, message_id)
    sender.send_and_deproto(
        client, chat_id, PURCHASE_DELETED, message_id, timeout=SERVICE_TIMEOUT
    )
