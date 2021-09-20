#!/usr/bin/env python3
from typing import List

from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from root.model.notification import Notification
from root.helper.notification import find_notifications_for_user
from telegram import Update
from telegram.chat import Chat
from telegram.ext import CallbackContext
from telegram.message import Message
from telegram.user import User
from root.util.util import create_button, format_date, format_time


def show_notifications(update: Update, context: CallbackContext):
    user: User = update.effective_user
    chat: Chat = update.effective_chat
    message: Message = update.effective_message
    notifications: List[Notification] = find_notifications_for_user(
        user.id, page_size=50
    )
    message = "<u><b>NOTIFICHE</b></u>\n\n"
    for notification in notifications:
        if notification.read:
            date = format_date(notification.creation_date)
            time = format_time(notification.creation_date, True)
            date = "%s %s" % (date, time)
            message += f"\n[{date}]  {notification.message}\n\n"
        else:
            message += f"\n🆕  [{date}]  <b>{notification.message}</b>\n\n"
    if update.callback_query:
        context.bot.edit_message_text(
            message_id=message.message_id,
            chat_id=chat.id,
            disable_web_page_preview=True,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        create_button(
                            "↩️  Torna indietro", "cancel_rating", "cancel_rating"
                        )
                    ]
                ]
            ),
        )
