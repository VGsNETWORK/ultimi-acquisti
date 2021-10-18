#!/usr/bin/env python3
from typing import List

from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from root.model.notification import Notification
from root.helper.notification import (
    find_notifications_for_user,
    mark_all_notification_as_read,
)
from telegram import Update
from telegram.chat import Chat
from telegram.ext import CallbackContext
from telegram.message import Message
from telegram.user import User
from root.util.util import create_button, format_date, format_time
import telegram_utils.utils.logger as logger


def show_notifications(update: Update, context: CallbackContext):
    logger.info("NOTIFICATIONS")
    user: User = update.effective_user
    chat: Chat = update.effective_chat
    message: Message = update.effective_message
    message_id = message.message_id
    notifications: List[Notification] = find_notifications_for_user(
        user.id, page_size=15
    )
    message = "<u><b>NOTIFICHE</b></u>\n\n"
    if notifications:
        for notification in notifications:
            date = format_date(notification.creation_date, show_year=True)
            time = format_time(notification.creation_date, True)
            date = "%s @ %s" % (date, time)
            if notification.read:
                message += f"\n<b>[{date}]</b>  {notification.message}\n\n"
            else:
                message += f"\n🆕  <b>[{date}]</b>  <b>{notification.message}</b>\n\n"
    else:
        message += "\n<i>Non hai ancora alcuna notifica da visualizzare.</i>"
    if update.callback_query:
        context.bot.edit_message_text(
            message_id=message_id,
            chat_id=chat.id,
            text=message,
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
        mark_all_notification_as_read(user.id)
