#!/usr/bin/env python3

""" File containing the function to delete a purchase """

import random
from datetime import datetime
from root.contants.keyboard import send_command_to_group_keyboard
from pyrogram.types.user_and_chats.chat_member import ChatMember
from telegram.user import User
from root.model.purchase import Purchase
from typing import List
from telegram import Update, Message, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from mongoengine.errors import DoesNotExist
from pyrogram.types import Message as PyroMessage
from pyrogram import Client
from root.util.util import get_month_number, get_month_string, is_group_allowed
from root.helper.user_helper import create_user, user_exists
import root.helper.purchase_helper as purchase_helper
from root.contants.messages import (
    CANCEL_PURCHASE_ERROR,
    ONLY_GROUP_QUOTE_SELF_PURCHASE,
    PURCHASES_DELETED,
    PURCHASES_DELETED_APPEND,
    PURCHASE_DELETED,
    ONLY_GROUP,
    PURCHASE_NOT_FOUND,
    NOT_YOUR_PURCHASE,
    NO_QUOTE_BOT,
    NOT_A_PURCHASE,
)
from root.util.telegram import TelegramSender
from root.contants.message_timeout import (
    ONE_MINUTE,
    SERVICE_TIMEOUT,
    LONG_SERVICE_TIMEOUT,
)
from root.util.util import create_button, retrieve_key
import root.util.logger as logger

sender = TelegramSender()


def delete_purchase(update: Update, context: CallbackContext) -> None:
    """delete a purchase from a user

    Args:
        update (Update): Telegram update
        context (CallbackContext): The context of the telegram bot
    """
    message: Message = update.message if update.message else update.edited_message
    command: str = message.text.split(" ")[0]
    command = command.split("@")[0]
    keyboard = send_command_to_group_keyboard(command)
    command = command.replace("/", "")
    if not sender.check_command(message):
        return
    sender.delete_if_private(context, message)
    chat_id = message.chat.id
    user = message.from_user
    if not user_exists(user.id):
        create_user(user)
    user_id = user.id
    first_name = user.first_name
    chat_type = message.chat.type
    if message.chat.type == "private":
        sender.send_and_delete(
            update.effective_message.message_id,
            update.effective_user.id,
            context,
            chat_id,
            ONLY_GROUP_QUOTE_SELF_PURCHASE % command,
            timeout=ONE_MINUTE,
            reply_markup=keyboard,
        )
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
        sender.send_and_delete(
            update.effective_message.message_id,
            update.effective_user.id,
            context,
            chat_id,
            message,
            timeout=SERVICE_TIMEOUT,
        )
        return
    if reply.from_user.is_bot:
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
    if not "#ultimiacquisti" in reply.text:
        message = NOT_A_PURCHASE % (user_id, first_name)
        bot_name = retrieve_key("BOT_NAME")
        keyboard = [
            [
                create_button(
                    "ℹ️  Scopri di più...",
                    callback="help_redirect",
                    query="help_redirect",
                    url=f"t.me/{bot_name}?start=how_to",
                )
            ]
        ]
        sender.send_and_delete(
            update.effective_message.message_id,
            update.effective_user.id,
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
            purchase: Purchase = purchase_helper.find_by_message_id_and_chat_id(
                message_id, message.chat.id
            )
            title = f"{purchase.description}" if purchase.description else "acquisto"
            title = title if title != "<vuoto>" else "acquisto"
            date: datetime = purchase.creation_date
            date = "%s %s" % (date.day, get_month_string(date.month, False, True))
            purchase_helper.delete_purchase(user_id, message_id)
            context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            name = user.first_name if user.first_name else user.username
            message = PURCHASE_DELETED % (user_id, name, title, date)
        else:
            message = NOT_YOUR_PURCHASE % (user_id, first_name)
        sender.send_and_delete(
            update.effective_message.message_id,
            update.effective_user.id,
            context,
            chat_id,
            message,
            timeout=SERVICE_TIMEOUT,
        )
    except DoesNotExist:
        message_id = message.message_id
        message = PURCHASE_NOT_FOUND % (user_id, first_name)
        sender.send_and_delete(
            update.effective_message.message_id,
            update.effective_user.id,
            context,
            chat_id,
            message,
            timeout=SERVICE_TIMEOUT,
        )


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


def deleted_purchase_message(client: Client, messages: List[PyroMessage]) -> None:
    """Remove the purchase from the database when a user deletes the message of a purchase

    Args:
        client (Client): The mtproto client
        message (PyroMessage): The mtproto Message
    """
    user_id = 0
    purchases = []
    titles = []
    for message in messages:
        message_id = message.message_id
        if purchase_helper.purchase_exists(message_id, message.chat.id):
            chat_id = message.chat.id
            purchase: Purchase = purchase_helper.find_by_message_id_and_chat_id(
                message_id, message.chat.id
            )
            user_id = purchase.user_id
            purchases.append(purchase.creation_date)
            titles.append(purchase.description)
            purchase_helper.delete_purchase_forced(message_id, message.chat.id)
    user: ChatMember = client.get_chat_member(chat_id, user_id)
    user: User = user.user
    message = PURCHASES_DELETED if len(messages) > 1 else PURCHASE_DELETED
    name = user.first_name if user.first_name else user.username
    if len(messages) > 1:
        message = message % (user_id, name, len(messages))
        append = []
        for purchase in zip(purchases, titles):
            title = f"{purchase[1]}" if purchase[1] else "acquisto"
            title = title if title != "<vuoto>" else "acquisto"
            date: datetime = purchase[0]
            date = "%s %s" % (date.day, get_month_string(date.month, False, True))
            append.append(PURCHASES_DELETED_APPEND % (title, date))
        message += "".join(append)
    else:
        title = f"{titles[0]}" if titles[0] else "acquisto"
        title = title if title != "<vuoto>" else "acquisto"
        date: datetime = purchases[0]
        date = "%s %s" % (date.day, get_month_string(date.month, False, True))
        message = message % (user_id, name, title, date)
    sender.send_and_deproto(
        client, chat_id, message, timeout=SERVICE_TIMEOUT * len(messages)
    )
