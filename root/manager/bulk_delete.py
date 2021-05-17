#!/usr/bin/env python3

import re
from root.util.util import retrieve_key
from root.helper.purchase_helper import (
    count_all_for_user_and_chat,
    delete_all_for_user_and_chat,
)
from root.helper.redis_message import add_message, is_owner
from root.contants.message_timeout import LONG_SERVICE_TIMEOUT
from root.contants.messages import (
    BULK_DELETE_CANCELLED,
    BULK_DELETE_MESSAGE,
    BULK_DELETE_NO_PURCHASESE,
    NOT_MESSAGE_OWNER,
    SESSION_ENDED,
)
from root.contants.keyboard import bulk_delete_keyboard
from telegram import Update
from telegram.chat import Chat
from telegram.ext import CallbackContext
from telegram import Message
import telegram_utils.utils.logger as logger
from root.util.telegram import TelegramSender

sender = TelegramSender()


def bulk_delete(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    bot_name: str = retrieve_key("BOT_NAME")
    message_text = re.sub("^\/\w+@", "", message.text)
    logger.info("private message with message_id: %s" % message.message_id)
    logger.info(message_text)
    logger.info(bot_name)
    if not bot_name == message_text and message.chat.type != "private":
        return
    message_id = message.message_id
    user = update.effective_user
    chat: Chat = update.effective_chat
    if chat.type == "private":
        return
    number_of_purchases = count_all_for_user_and_chat(user.id, chat.id)
    logger.info(number_of_purchases)
    if number_of_purchases == 0:
        sender.send_and_delete(
            message_id,
            update.effective_user.id,
            context,
            chat_id=chat.id,
            text=BULK_DELETE_NO_PURCHASESE % user.first_name,
            timeout=LONG_SERVICE_TIMEOUT,
        )
        return
    if update.callback_query:
        step = update.callback_query.data
        step = int(step.split("_")[-1])
    else:
        step = 0

    if step > 0:
        try:
            if is_owner(message_id, user.id):
                context.bot.answer_callback_query(update.callback_query.id)
            else:
                context.bot.answer_callback_query(
                    update.callback_query.id,
                    text=NOT_MESSAGE_OWNER,
                    show_alert=True,
                )
                return
        except ValueError:
            context.bot.answer_callback_query(
                update.callback_query.id,
                text=SESSION_ENDED,
                show_alert=True,
            )
            context.bot.delete_message(chat_id=chat.id, message_id=message_id)
            return

    if step == 0:
        message = BULK_DELETE_MESSAGE[step] % chat.title.split(" | ")[0]
    elif step == 1:
        message = BULK_DELETE_MESSAGE[step] % number_of_purchases
    else:
        message = BULK_DELETE_MESSAGE[step]
    keyboard = bulk_delete_keyboard(step + 1)
    if step == 3:
        # do the magic
        delete_all_for_user_and_chat(user.id, chat.id)
        sender.edit_and_delete(
            update.effective_message.message_id,
            context,
            update.effective_chat.id,
            message,
            timeout=LONG_SERVICE_TIMEOUT,
        )
        return
    if step == 0:
        message: Message = context.bot.send_message(
            chat_id=chat.id,
            text=message,
            reply_markup=keyboard,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
        add_message(message.message_id, user.id, False)
    else:
        context.bot.edit_message_text(
            chat_id=chat.id,
            message_id=message_id,
            text=message,
            reply_markup=keyboard,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )


def cancel_bulk_delete(update: Update, context: CallbackContext):
    sender.edit_and_delete(
        update.effective_message.message_id,
        context,
        update.effective_chat.id,
        BULK_DELETE_CANCELLED,
        timeout=LONG_SERVICE_TIMEOUT,
    )
