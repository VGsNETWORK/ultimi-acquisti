#!/usr/bin/env python3

from typing import List
from telegram.error import BadRequest
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.ext.conversationhandler import ConversationHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
import telegram_utils.utils.logger as logger
from telegram_utils.utils.tutils import delete_if_private
from root.contants.keyboard import (
    build_admin_communication_keyboard,
    build_ask_communication_delete_keyboard,
)
from root.contants.messages import (
    ADMIN_COMMUNICATION_DELETION_CONFIRMATION,
    ADMIN_PANEL_MAIN_MESSAGE,
    COMMUNICATION_DELETION_CONFIRMATION,
    NEW_COMMUNICATION_CREATED,
    NO_COMMUNICATION_MESSAGE,
    USER_INFO_RECAP_LEGEND,
)
from root.helper import keyboard
from root.helper.admin_message import (
    create_admin_message,
    find_admin_message_by_id,
    get_paged_admin_messages,
    get_total_admin_messages,
    purge_admin_message,
)
from root.helper.aggregation.user_info import USER_INFO_NATIVE_QUERY
from root.model.admin_message import AdminMessage
from root.model.user import User
from root.model.wishlist import Wishlist
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
import telegram_utils.helper.redis as redis_helper

SEND_COMMUNICATION = range(1)

ADMIN_PANEL_KEYBOARD = InlineKeyboardMarkup(
    [
        [create_button("📨  Comunicazioni", "show_admin_messages", None)],
        [create_button("📊  Vedi le statistiche", "show_usage", None)],
        [create_button("↩️  Torna indietro", "cancel_rating", None)],
    ]
)

INIT_SEND_COMMUNICATION_KEYBOARD = InlineKeyboardMarkup(
    [[create_button("❌  Annulla", "cancel_send_comunication", None)]]
)


def resend_communication(update: Update, context: CallbackContext):
    data: str = update.callback_query.data
    page = int(data.split("_")[-1])
    communication_id = data.split("_")[-2]
    communication: AdminMessage = find_admin_message_by_id(communication_id)
    if communication:
        create_admin_message(communication.message)
    show_admin_messages(update, context, page)


def navigate_admin_notifications(update: Update, context: CallbackContext):
    data: str = update.callback_query.data
    page = int(data.split("_")[-1])
    communication_id = data.split("_")[-2]
    total_pages = get_total_admin_messages()
    if communication_id != "NONE":
        communication: AdminMessage = find_admin_message_by_id(communication_id)
    else:
        communication = None
    if page < 0:
        page = 0
    if page > total_pages - 1:
        page = total_pages - 1
    show_admin_messages(update, context, page, communication)


def view_admin_comunication(update: Update, context: CallbackContext):
    data: str = update.callback_query.data
    page = int(data.split("_")[-1])
    communication_id = data.split("_")[-2]
    admin_message: AdminMessage = find_admin_message_by_id(communication_id)
    total_pages = get_total_admin_messages()
    if page < 0:
        page = 0
    if page > total_pages - 1:
        page = total_pages - 1
    logger.info(admin_message)
    logger.info(admin_message.message)
    show_admin_messages(update, context, page, admin_message)


def ask_delete_admin_communication(update: Update, context: CallbackContext):
    data: str = update.callback_query.data
    page = int(data.split("_")[-1])
    communication_id = data.split("_")[-2]
    communication: AdminMessage = find_admin_message_by_id(communication_id)
    message = "<b><u>PANNELLO ADMIN</u>    ➔    COMUNICAZIONI</b>\n\n\n"
    date = communication.creation_date
    date = "Inviato %s%s alle %s" % (
        get_article(date),
        format_date(date, True),
        format_time(date, True),
    )
    message += f'"{communication.message}"\n\n<i>{date}</i>'
    message += ADMIN_COMMUNICATION_DELETION_CONFIRMATION
    context.bot.edit_message_text(
        message_id=update.effective_message.message_id,
        chat_id=update.effective_chat.id,
        text=message,
        disable_web_page_preview=True,
        parse_mode="HTML",
        reply_markup=build_ask_communication_delete_keyboard(
            communication_id, page, True
        ),
    )


def delete_admin_communication(update: Update, context: CallbackContext):
    data: str = update.callback_query.data
    page = int(data.split("_")[-1])
    communication_id = data.split("_")[-2]
    purge_admin_message(communication_id)
    show_admin_messages(update, context, page, None)


def show_admin_messages(
    update: Update,
    context: CallbackContext,
    page: int = 0,
    communication: AdminMessage = None,
    alert: str = None,
):
    logger.info("NOTIFICATIONS")
    user: User = update.effective_user
    chat: Chat = update.effective_chat
    message: Message = update.effective_message
    message_id = message.message_id
    total_pages = get_total_admin_messages()
    admin_messages: List[AdminMessage] = get_paged_admin_messages(page)
    logger.info(f"TOTAL PAGES: {total_pages}, PAGE: {page}")
    if page == total_pages:
        if not admin_messages:
            page -= 1
            admin_messages: List[AdminMessage] = get_paged_admin_messages(page)
    message = "<b><u>PANNELLO ADMIN</u>    ➔    COMUNICAZIONI</b>\n\n\n"
    if admin_messages:
        if not communication:
            message += NO_COMMUNICATION_MESSAGE
        else:
            date = communication.creation_date
            date = "Inviato %s%s alle %s" % (
                get_article(date),
                format_date(date, True),
                format_time(date, True),
            )
            message += f'"{communication.message}"\n\n\n<b><i>{date}</i></b>'
    else:
        message += NO_COMMUNICATION_MESSAGE
    communication_id = str(communication.id) if communication else ""
    keyboard = build_admin_communication_keyboard(
        admin_messages, communication_id, page, total_pages
    )
    if not update.callback_query:
        message_id = redis_helper.retrieve("%s_%s_admin" % (user.id, user.id)).decode()
    if alert:
        message += alert
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
    except BadRequest as e:
        logger.error(e)
    return ConversationHandler.END


def handle_admin(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    message_id = message.message_id
    try:
        context.bot.edit_message_text(
            chat_id=chat.id,
            message_id=message_id,
            text=ADMIN_PANEL_MAIN_MESSAGE,
            reply_markup=ADMIN_PANEL_KEYBOARD,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except BadRequest:
        user = update.effective_user
        try:
            context.bot.edit_message_text(
                message_id=redis_helper.retrieve(
                    "%s_%s_admin" % (user.id, user.id)
                ).decode(),
                chat_id=update.effective_chat.id,
                text=ADMIN_PANEL_MAIN_MESSAGE,
                disable_web_page_preview=True,
                reply_markup=ADMIN_PANEL_KEYBOARD,
                parse_mode="HTML",
            )
        except Exception as e:
            logger.error(e)
    return ConversationHandler.END


def show_usage(update: Update, context: CallbackContext):
    cursor = Wishlist.objects.aggregate(USER_INFO_NATIVE_QUERY)
    message = ""
    for result in cursor:
        logger.info(result)
        try:
            if "last_name" in result:
                name = "%s %s" % (result["first_name"], result["last_name"])
            else:
                name = "%s" % (result["first_name"])
        except KeyError:
            name = "<i>&lt;Sconosciuto&gt;</i>"
        try:
            line = '<a href="tg://user?id=%s">%s  (@%s)</a>' % (
                result["user_id"],
                name,
                result["username"],
            )
        except KeyError:
            line = '<a href="tg://user?id=%s">%s</a>' % (
                result["user_id"],
                name,
            )
        line += "\n    🗃  <code>%s</code>" % result["wishlists"]
        line += "\n     │"
        line += "\n     └─🗂  <code>%s</code>" % result["wishlist_elements"]
        line += "\n            │"
        line += "\n            ├─🖼  <code>%s</code>" % result["photos"]
        line += "\n            │"
        line += "\n            └─🔗  <code>%s</code>" % result["links"]
        line += "\n                   │"
        line += "\n                   └─💹  <code>%s</code>" % result["tracked_links"]
        line += "\n\n\n"
        message += line
    message += USER_INFO_RECAP_LEGEND
    message = f"<b><u>PANNELLO ADMIN</u>    ➔    STATISTICHE</b>\n\n\n{message}"
    keyboard = InlineKeyboardMarkup(
        [[create_button("↩️  Torna indietro", "show_admin_panel", "")]]
    )
    try:
        context.bot.edit_message_text(
            message_id=update.effective_message.message_id,
            chat_id=update.effective_chat.id,
            text=message,
            disable_web_page_preview=True,
            reply_markup=keyboard,
            parse_mode="HTML",
        )
    except BadRequest:
        user = update.effective_user
        try:
            context.bot.edit_message_text(
                message_id=redis_helper.retrieve(
                    "%s_%s_admin" % (user.id, user.id)
                ).decode(),
                chat_id=update.effective_chat.id,
                text=message,
                disable_web_page_preview=True,
                reply_markup=keyboard,
                parse_mode="HTML",
            )
        except Exception as e:
            logger.error(e)
    return context.bot.answer_callback_query(update.callback_query.id)


def init_send_comunication(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    message_id = message.message_id
    redis_helper.save("%s_%s_admin" % (user.id, user.id), str(message_id))
    message = "<b><u>PANNELLO ADMIN</u>    ➔    NUOVA COMUNICAZIONE</b>\n\n\n"
    message += "Inserisci il messaggio da inviare in broadcast:"
    context.bot.edit_message_text(
        chat_id=chat.id,
        message_id=message_id,
        text=message,
        disable_web_page_preview=True,
        reply_markup=INIT_SEND_COMMUNICATION_KEYBOARD,
        parse_mode="HTML",
    )
    return SEND_COMMUNICATION


def send_comunication(update: Update, context: CallbackContext):
    text = update.effective_message.text
    delete_if_private(update.effective_message)
    create_admin_message(text)
    show_admin_messages(update, context, alert=NEW_COMMUNICATION_CREATED)
    return ConversationHandler.END


SEND_COMUNICATION_CONVERSTATION = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            pattern="send_comunication", callback=init_send_comunication
        )
    ],
    states={SEND_COMMUNICATION: [MessageHandler(Filters.text, send_comunication)]},
    fallbacks=[
        CallbackQueryHandler(show_admin_messages, pattern="cancel_send_comunication"),
    ],
)