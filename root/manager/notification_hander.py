#!/usr/bin/env python3
from typing import List
from telegram.error import BadRequest

import telegram_utils.utils.logger as logger
from root.contants.keyboard import build_notification_choose_section
from root.helper.admin_message import (
    count_unread_admin_messages_for_user,
    find_admin_message_by_id,
    get_paged_unread_messages,
    get_total_unread_messages,
    get_unread_admin_messages_for_user,
    read_admin_message,
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


def navigate_notifications(update: Update, context: CallbackContext):
    data: str = update.callback_query.data
    page = int(data.split("_")[-1])
    total_pages = get_total_unread_messages(update.effective_user.id)
    if page < 0:
        page = 0
    if page > total_pages - 1:
        page = total_pages - 1
    show_messages(update, context, page)


def view_comunication(update: Update, context: CallbackContext):
    data: str = update.callback_query.data
    page = int(data.split("_")[-1])
    communication_id = data.split("_")[-2]
    admin_message: AdminMessage = find_admin_message_by_id(communication_id)
    total_pages = get_total_unread_messages(update.effective_user.id)
    if page < 0:
        page = 0
    if page > total_pages - 1:
        page = total_pages - 1
    logger.info(admin_message)
    logger.info(admin_message.message)
    read_admin_message(update.effective_user.id, communication_id)
    show_messages(update, context, page, admin_message)


def show_messages(
    update: Update,
    context: CallbackContext,
    page: int = 0,
    communication: AdminMessage = None,
):
    logger.info("NOTIFICATIONS")
    user: User = update.effective_user
    chat: Chat = update.effective_chat
    message: Message = update.effective_message
    message_id = message.message_id
    admin_messages: List[AdminMessage] = get_paged_unread_messages(user.id, page)
    total_pages = get_total_unread_messages(user.id)
    message = "<b><u>CENTRO MESSAGGI</u>    ➔    COMUNICAZIONI</b>\n\n\n"
    if admin_messages:
        if not communication:
            message += "<i>Seleziona una comunicazione da visualizzare:</i>"
        else:
            date = communication.creation_date
            date = "Inviato il %s alle %s" % (
                format_date(date, True),
                format_time(date),
            )
            message += f'"{communication.message}"\n\n\n<b><i>{date}</i></b>'
    else:
        message += "\n<i>Non hai ancora alcuna comunicazione da visualizzare.</i>"
    nof_notifications = count_unread_notifications(user.id)
    nof_messages = count_unread_admin_messages_for_user(user.id)
    keyboard = build_notification_choose_section(
        nof_notifications,
        nof_messages,
        1,
        admin_messages,
        update.effective_user.id,
        page,
        total_pages,
        str(communication.id if communication else ""),
    )
    if update.callback_query:
        try:
            context.bot.edit_message_text(
                message_id=message_id,
                chat_id=chat.id,
                text=message,
                disable_web_page_preview=True,
                parse_mode="HTML",
                reply_markup=keyboard,
            )
        except BadRequest:
            pass


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
