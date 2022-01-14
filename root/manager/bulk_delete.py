#!/usr/bin/env python3

import re
from root.manager.start import back_to_the_start
from root.util.util import append_timeout_message, retrieve_key
from root.helper.purchase_helper import (
    count_all_for_user_and_chat,
    delete_all_for_user_and_chat,
)
from root.helper.redis_message import add_message, is_owner
from root.contants.message_timeout import (
    LONG_SERVICE_TIMEOUT,
    ONE_MINUTE,
    SERVICE_TIMEOUT,
)
from root.contants.messages import (
    BULK_DELETE_CANCELLED,
    BULK_DELETE_MESSAGE,
    BULK_DELETE_MESSAGE_SINGLE_PURCHASE,
    BULK_DELETE_NO_PURCHASE,
    NOT_MESSAGE_OWNER,
    NO_GROUP_PURCHASE,
    ONLY_GROUP_NO_QUOTE,
    SESSION_ENDED,
)
from root.contants.keyboard import (
    NO_PURCHASE_KEYBOARD,
    bulk_delete_keyboard,
    send_command_to_group_keyboard,
)
from telegram import Update
from telegram.chat import Chat
from telegram.ext import CallbackContext
from telegram import Message
import telegram_utils.utils.logger as logger
from root.util.telegram import TelegramSender
from bot_util.decorator.maintenance import check_maintenance
sender = TelegramSender()

@check_maintenance
def bulk_delete(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    bot_name: str = retrieve_key("BOT_NAME")
    command = message.text.split("@")[0]
    command = command.replace("/", "")
    message_text = re.sub("^\/\w+@", "", message.text)
    logger.info("private message with message_id: %s" % message.message_id)
    message_id = message.message_id
    user = update.effective_user
    chat: Chat = update.effective_chat
    if message.text.startswith("/"):
        if not bot_name == message_text and message.chat.type != "private":
            return
    if chat.type == "private":
        sender.delete_if_private(context, message)
        message = ONLY_GROUP_NO_QUOTE % command
        message = append_timeout_message(message, False, ONE_MINUTE, True)
        sender.send_and_edit(
            update,
            context,
            chat.id,
            callback=back_to_the_start,
            text=message,
            timeout=ONE_MINUTE,
            reply_markup=send_command_to_group_keyboard("%2F" + command),
        )
        return
    number_of_purchases = count_all_for_user_and_chat(user.id, chat.id)
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

    if number_of_purchases == 0:
        sender.send_and_delete(
            message_id,
            update.effective_user.id,
            context,
            chat_id=chat.id,
            text=NO_GROUP_PURCHASE % (user.id, user.first_name),
            reply_markup=NO_PURCHASE_KEYBOARD,
            timeout=ONE_MINUTE,
        )
        return

    if step == 0:
        message = BULK_DELETE_MESSAGE[step] % chat.title.split(" | ")[0]
    elif step == 1:
        if number_of_purchases != 1:
            if number_of_purchases in [8, 11]:
                append = "gli"
            else:
                append = "i"
            message = BULK_DELETE_MESSAGE[step] % (append, number_of_purchases)
        else:
            message = BULK_DELETE_MESSAGE_SINGLE_PURCHASE
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

@check_maintenance
def cancel_bulk_delete(update: Update, context: CallbackContext):
    message_id = update.effective_message.message_id
    user = update.effective_user
    chat = update.effective_chat
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

    sender.edit_and_delete(
        update.effective_message.message_id,
        context,
        update.effective_chat.id,
        BULK_DELETE_CANCELLED,
        timeout=SERVICE_TIMEOUT,
    )
