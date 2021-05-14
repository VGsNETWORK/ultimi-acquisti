#!/usr/bin/env python3

""" File to retrieve the last purchase of the user """

from root.contants.keyboard import NO_PURCHASE_KEYBOARD
from telegram import Update, Message
from telegram.ext import CallbackContext
from telegram.error import BadRequest
import root.util.logger as logger
from root.util.util import append_timeout_message, format_price
from root.model.purchase import Purchase
from root.helper.purchase_helper import get_last_purchase
from root.contants.messages import (
    LAST_PURCHASE,
    NO_PURCHASE,
    NO_QUOTE_BOT,
    LAST_PURCHASE_USER,
    PURCHASE_RECAP_APPEND,
)
from root.contants.message_timeout import (
    SERVICE_TIMEOUT,
    ONE_MINUTE,
    TWO_MINUTES,
)
from root.util.telegram import TelegramSender
from root.manager.start import back_to_the_start

sender = TelegramSender()


def last_purchase(update: Update, context: CallbackContext) -> None:
    """ Retrieve the last purchase of the user who typed the command """
    logger.info("received command last purchase")
    message: Message = update.message if update.message else update.edited_message
    if not sender.check_command(message):
        return
    sender.delete_if_private(context, message)
    chat_id = message.chat.id
    chat_type = message.chat.type
    user = update.effective_user
    user_id = user.id
    first_name = user.first_name
    if user.is_bot:
        message: str = NO_QUOTE_BOT % (user_id, user.first_name)
        sender.send_and_delete(
            update.effective_message.message_id,
            update.effective_user.id,
            context,
            chat_id,
            message,
            SERVICE_TIMEOUT,
        )
        return
    purchase: Purchase = get_last_purchase(user_id)
    if message.reply_to_message:
        rmessage: Message = message.reply_to_message
        ruser = rmessage.from_user
        if ruser.is_bot:
            message: str = NO_QUOTE_BOT % (user_id, user.first_name)
            sender.send_and_delete(
                update.effective_message.message_id,
                update.effective_user.id,
                context,
                chat_id,
                message,
                SERVICE_TIMEOUT,
            )
            return
        user_id = ruser.id
        first_name = ruser.first_name
    purchase = get_last_purchase(user_id)
    is_private = not update.effective_chat.type == "private"
    if purchase:
        purchase_chat_id = str(purchase.chat_id).replace("-100", "")
        date = purchase.creation_date
        time = date.strftime("%H:%M")
        date = date.strftime("%d/%m/%Y")
        if not message.reply_to_message or user.id == user_id:
            recap = PURCHASE_RECAP_APPEND(
                format_price(purchase.price),
                purchase.description,
                None,
            )
            message = LAST_PURCHASE % (
                user_id,
                first_name,
                date,
                time,
                recap,
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
            logger.info("HERE")
            sender.send_and_delete(
                update.effective_message.message_id,
                update.effective_user.id,
                context,
                chat_id,
                message,
                reply_to_message_id=purchase.message_id,
                timeout=TWO_MINUTES,
            )
        except BadRequest:
            if chat_type == "private":
                message = append_timeout_message(
                    message, is_private, ONE_MINUTE, is_private
                )
                sender.send_and_edit(
                    update,
                    context,
                    chat_id,
                    message,
                    back_to_the_start,
                    timeout=TWO_MINUTES,
                )
                return

            sender.send_and_delete(
                update.effective_message.message_id,
                update.effective_user.id,
                context,
                chat_id,
                message,
                timeout=TWO_MINUTES,
            )
    else:
        message = NO_PURCHASE % (user_id, first_name)
        if chat_type == "private":
            message = append_timeout_message(
                message, is_private, ONE_MINUTE, is_private
            )
            sender.send_and_edit(
                update,
                context,
                chat_id,
                message,
                back_to_the_start,
                reply_markup=NO_PURCHASE_KEYBOARD,
                timeout=ONE_MINUTE,
            )
            return

        sender.send_and_delete(
            update.effective_message.message_id,
            update.effective_user.id,
            context,
            chat_id,
            message,
            reply_markup=NO_PURCHASE_KEYBOARD,
            timeout=ONE_MINUTE,
        )
