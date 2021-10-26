#!/usr/bin/env python3
from typing import List

import telegram_utils.utils.logger as logger
from root.contants.keyboard import build_notification_choose_section
from root.helper.admin_message import (
    count_unread_admin_messages_for_user,
    get_unread_admin_messages_for_user,
)
from root.helper.notification import (
    count_unread_notifications,
    find_notifications_for_user,
    mark_all_notification_as_read,
)
from root.model.admin_message import AdminMessage
from root.model.notification import Notification
from root.util.util import create_button, format_date, format_time
from telegram import Update
from telegram.chat import Chat
from telegram.ext import CallbackContext
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.message import Message
from telegram.user import User


def open_notification_panel(update: Update, context: CallbackContext):
    show_notifications(update, context)


def show_messages(update: Update, context: CallbackContext):
    logger.info("NOTIFICATIONS")
    user: User = update.effective_user
    chat: Chat = update.effective_chat
    message: Message = update.effective_message
    message_id = message.message_id
    admin_messages: List[AdminMessage] = get_unread_admin_messages_for_user(user.id)
    message = "<b><u>CENTRO MESSAGGI</u>    ➔    COMUNICAZIONI</b>\n\n"
    if admin_messages:
        for admin_message in admin_messages:
            date = format_date(admin_message.creation_date, show_year=True)
            time = format_time(admin_message.creation_date, True)
            date = "%s @ %s" % (date, time)
            if user.id in admin_message.read:
                message += f"\n<b>[{date}]</b>  {admin_message.message}\n\n"
            else:
                message += f"\n🆕  <b>[{date}]</b>  <b>{admin_message.message}</b>\n\n"
    else:
        message += "\n<i>Non hai ancora alcuna comunicazione da visualizzare.</i>"
    nof_notifications = count_unread_notifications(user.id)
    nof_messages = count_unread_admin_messages_for_user(user.id)
    keyboard = build_notification_choose_section(nof_notifications, nof_messages, 1)
    if update.callback_query:
        context.bot.edit_message_text(
            message_id=message_id,
            chat_id=chat.id,
            text=message,
            disable_web_page_preview=True,
            parse_mode="HTML",
            reply_markup=keyboard,
        )
        mark_all_notification_as_read(user.id)


def show_notifications(update: Update, context: CallbackContext):
    logger.info("NOTIFICATIONS")
    user: User = update.effective_user
    chat: Chat = update.effective_chat
    message: Message = update.effective_message
    message_id = message.message_id
    notifications: List[Notification] = find_notifications_for_user(
        user.id, page_size=15
    )
    message = "<b><u>CENTRO MESSAGGI</u>    ➔    NOTIFICHE</b>\n\n"
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
    nof_notifications = count_unread_notifications(user.id)
    nof_messages = count_unread_admin_messages_for_user(user.id)
    keyboard = build_notification_choose_section(nof_notifications, nof_messages)
    if update.callback_query:
        context.bot.edit_message_text(
            message_id=message_id,
            chat_id=chat.id,
            text=message,
            disable_web_page_preview=True,
            parse_mode="HTML",
            reply_markup=keyboard,
        )
        mark_all_notification_as_read(user.id)
