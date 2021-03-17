#!/usr/bin/env python3

""" File with functions shared between various reports """

from telegram import Update
from telegram.ext import CallbackContext
from root.contants.messages import NOT_MESSAGE_OWNER, SESSION_ENDED
from root.helper.process_helper import restart_process
from root.helper.redis_message import is_owner
from root.util.telegram import TelegramSender

sender = TelegramSender()


def check_owner(update: Update, context: CallbackContext) -> bool:
    """Check and stop not owner of the report

    Args:
        update (Update): Telegram update
            context (CallbackContext): The context of the telegram bot

    Returns:
        bool: True if is the owner, False otherwise
    """
    user = update.effective_user
    message_id = update.effective_message.message_id
    chat_id = update.effective_chat.id
    user_id = user.id
    try:
        if not is_owner(message_id, user_id):
            context.bot.answer_callback_query(
                update.callback_query.id, text=NOT_MESSAGE_OWNER, show_alert=True
            )
            return False
    except ValueError:
        context.bot.answer_callback_query(
            update.callback_query.id, text=SESSION_ENDED, show_alert=True
        )
        sender.delete_message(context, chat_id, message_id)
        return False
    restart_process(message_id)
    context.bot.answer_callback_query(update.callback_query.id)
    return True
