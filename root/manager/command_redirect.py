#!/usr/bin/env python3

from root.contants.messages import DEEP_LINK, ONLY_PRIVATE
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.user import User
from root.contants.message_timeout import ONE_MINUTE
from root.util.util import append_timeout_message, create_button, retrieve_key
from telegram import Update
from telegram.ext import CallbackContext
from root.util.telegram import TelegramSender

sender = TelegramSender()


def command_redirect(
    command: str, callback: str, update: Update, context: CallbackContext
):
    if not sender.check_command(update.effective_message):
        return
    user: User = update.effective_user
    user_id: int = user.id
    chat_id: int = update.effective_chat.id
    first_name: str = user.first_name

    bot_name = retrieve_key("BOT_NAME")

    deep_link = DEEP_LINK % (bot_name, callback)

    message = ONLY_PRIVATE % command

    button = create_button(
        message='Comando "%s" in chat privata' % command,
        callback="button_redirect",
        query="button_redirect",
        url=f"t.me/{bot_name}?start=%s" % callback,
    )

    sender.send_and_delete(
        update.effective_message.message_id,
        update.effective_user.id,
        context,
        chat_id,
        message,
        reply_markup=InlineKeyboardMarkup([[button]]),
        timeout=ONE_MINUTE,
    )