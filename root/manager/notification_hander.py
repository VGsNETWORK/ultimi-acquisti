#!/usr/bin/env python3
from typing import List
from bot_util.decorator.telegram import update_user_information
from telegram.error import BadRequest

import telegram_utils.utils.logger as logger
from root.contants.keyboard import (
    build_ask_communication_delete_keyboard,
    build_notification_choose_section,
)
from root.contants.messages import (
    COMMUNICATION_DELETION_CONFIRMATION,
    COMMUNICATION_SENT_DATE_TIME_MESSAGE,
    NO_COMMUNICATION_MESSAGE,
    NO_COMMUNICATION_SELECTED_MESSAGE,
    NO_NOTIFICATION_TO_VIEW,
    NOTIFICATION_COMMUNICATION_HEADER,
    NOTIFICATION_MESSAGE_FORMAT,
    NOTIFICATION_NOTIFICATION_HEADER,
    NOTIFICATION_READ_FORMAT,
    NOTIFICATION_UNREAD_FORMAT,
)
from root.helper.admin_message import (
    count_unread_admin_messages_for_user,
    delete_admin_message,
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
from root.helper.start_messages import delete_start_message
from root.model.admin_message import AdminMessage
from root.model.notification import Notification
from root.util.util import (
    create_button,
    format_date,
    format_time,
    generate_random_invisible_char,
    get_article,
)
from telegram import Update
from telegram.chat import Chat
from telegram.ext import CallbackContext
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.message import Message
from telegram.user import User


def open_notification_panel(update: Update, context: CallbackContext):
    if update.effective_message.chat.type == "private":
        delete_start_message(update.effective_user.id)
    show_messages(update, context)


def navigate_notifications(update: Update, context: CallbackContext):
    data: str = update.callback_query.data
    page = int(data.split("_")[-1])
    communication_id = data.split("_")[-2]
    if communication_id != "NONE":
        communication: AdminMessage = find_admin_message_by_id(communication_id)
    else:
        communication = None
    total_pages = get_total_unread_messages(update.effective_user.id)
    if page < 0:
        page = 0
    if page > total_pages - 1:
        page = total_pages - 1
    show_messages(update, context, page, communication)


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


def ask_delete_communication(update: Update, context: CallbackContext):
    data: str = update.callback_query.data
    page = int(data.split("_")[-1])
    communication_id = data.split("_")[-2]
    communication: AdminMessage = find_admin_message_by_id(communication_id)
    message = NOTIFICATION_COMMUNICATION_HEADER
    date = communication.creation_date
    date = COMMUNICATION_SENT_DATE_TIME_MESSAGE % (
        get_article(date),
        format_date(date, True),
        format_time(date, True),
    )
    message += f'"{communication.message}"\n\n<i>{date}</i>'
    message += COMMUNICATION_DELETION_CONFIRMATION
    context.bot.edit_message_text(
        message_id=update.effective_message.message_id,
        chat_id=update.effective_chat.id,
        text=message,
        disable_web_page_preview=True,
        parse_mode="HTML",
        reply_markup=build_ask_communication_delete_keyboard(communication_id, page),
    )


def delete_communication(update: Update, context: CallbackContext):
    data: str = update.callback_query.data
    page = int(data.split("_")[-1])
    communication_id = data.split("_")[-2]
    delete_admin_message(update.effective_user.id, communication_id)
    show_messages(update, context, page)


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
    total_pages = get_total_unread_messages(user.id)
    admin_messages: List[AdminMessage] = get_paged_unread_messages(user.id, page)
    if page == total_pages:
        if not admin_messages:
            page -= 1
            admin_messages: List[AdminMessage] = get_paged_unread_messages(
                user.id, page
            )
    message = NOTIFICATION_COMMUNICATION_HEADER
    if admin_messages:
        if not communication:
            message += NO_COMMUNICATION_SELECTED_MESSAGE
        else:
            date = communication.creation_date
            date = COMMUNICATION_SENT_DATE_TIME_MESSAGE % (
                get_article(date),
                format_date(date, True),
                format_time(date, True),
            )
            message += NOTIFICATION_MESSAGE_FORMAT % (communication.message, date)
    else:
        message += NO_COMMUNICATION_MESSAGE
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
        message += generate_random_invisible_char(user.id)
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
    user: User = update.effective_user
    chat: Chat = update.effective_chat
    message: Message = update.effective_message
    message_id = message.message_id
    notifications: List[Notification] = find_notifications_for_user(
        user.id, page_size=15
    )
    message = NOTIFICATION_NOTIFICATION_HEADER
    if notifications:
        for notification in notifications:
            date = format_date(notification.creation_date, show_year=True)
            time = format_time(notification.creation_date, True)
            date = "%s @ %s" % (date, time)
            if notification.read:
                message += NOTIFICATION_READ_FORMAT % (date, notification.message)
            else:
                message += NOTIFICATION_UNREAD_FORMAT % (date, notification.message)
    else:
        message += NO_NOTIFICATION_TO_VIEW
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
