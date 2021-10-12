#!/usr/bin/env python3

import re
from typing import List
from root.contants.keyboard import GROUP_START_KEYBOARD
from root.contants.message_timeout import THIRTY_MINUTES
from root.helper.whitelist_helper import is_whitelisted, whitelist_chat
from root.contants.messages import (
    BOT_ADDED_WELCOME_APPEND,
    BOT_ADDED_WELCOME_MESSAGE,
    BOT_ID,
    GROUP_NOT_ALLOWED,
)
from telegram import Update
from telegram.chat import Chat
from telegram.ext import CallbackContext
from telegram.message import Message
from telegram.user import User
from root.helper.user_helper import retrieve_user
import telegram_utils.utils.logger as logger
from telegram import ChatMember
from root.util.telegram import TelegramSender


sender = TelegramSender()


def handle_new_group(update: Update, context: CallbackContext):
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    message: Message = update.effective_message
    db_user = retrieve_user(user.id)
    chat_members: List[ChatMember] = update.effective_message.new_chat_members
    if chat_members:
        is_bot = next((member.id == int(BOT_ID) for member in chat_members), False)
        if not is_bot:
            return
    if db_user.is_admin:
        if not is_whitelisted(chat.id):
            logger.info("Whitelisto la seguente chat %s." % chat.id)
            whitelist_chat(chat.id)
        else:
            logger.info("La chat %s è già whitelistata." % chat.id)
        group_name = update.effective_chat.title
        group_name = re.sub(r"\s?\|.*$", "", group_name)
        welcome_message = BOT_ADDED_WELCOME_MESSAGE % (
            group_name,
            BOT_ADDED_WELCOME_APPEND,
        )
        sender.send_and_delete(
            message.message_id,
            user.id,
            context,
            chat.id,
            welcome_message,
            reply_markup=GROUP_START_KEYBOARD,
            timeout=THIRTY_MINUTES,
        )

    else:
        logger.info("L'utente %s non è admin del bot." % user.id)
        context.bot.send_message(
            chat_id=chat.id,
            text=GROUP_NOT_ALLOWED,
            parse_mode="HTML",
        )
        context.bot.send_message(
            chat_id=chat.id,
            text="🍃  So long suckers!!!",
        )
        context.bot.leave_chat(chat.id)
