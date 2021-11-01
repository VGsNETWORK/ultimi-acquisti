#!/usr/bin/env python3

from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.ext.conversationhandler import ConversationHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram_utils.utils.tutils import delete_if_private
from root.contants.keyboard import (
    build_ask_communication_delete_keyboard,
    build_resent_prompt_keyboard,
)
from root.contants.messages import ADMIN_RESEND_NOTIFICATION_CONFIRMATION
from root.helper.admin_message import create_admin_message, find_admin_message_by_id
from root.manager.admin_handler import show_admin_messages
from root.model.admin_message import AdminMessage
from root.util.util import format_date, format_time, get_article
import telegram_utils.utils.logger as logger
import telegram_utils.helper.redis as redis_helper


RESEND_COMMUNICATION = range(1)


def ask_resend_communication(update: Update, context: CallbackContext):
    data = update.callback_query.data
    user = update.effective_user
    communication_id = data.split("_")[-2]
    page = data.split("_")[-1]
    communication: AdminMessage = find_admin_message_by_id(communication_id)
    message = "<b><u>PANNELLO ADMIN</u>    ➔    COMUNICAZIONI</b>\n\n\n"
    date = communication.creation_date
    date = "Inviato %s%s alle %s" % (
        get_article(date),
        format_date(date, True),
        format_time(date, True),
    )
    redis_helper.save(
        "%s_%s_admin" % (user.id, user.id), str(update.effective_message.message_id)
    )
    message += f'"<code>{communication.message}</code>"\n\n<i>{date}</i>'
    message += ADMIN_RESEND_NOTIFICATION_CONFIRMATION
    context.bot.edit_message_text(
        message_id=update.effective_message.message_id,
        chat_id=update.effective_chat.id,
        text=message,
        disable_web_page_preview=True,
        parse_mode="HTML",
        reply_markup=build_resent_prompt_keyboard(communication_id, page),
    )
    return RESEND_COMMUNICATION


def resend_commumication(update: Update, context: CallbackContext):
    logger.info("RESEND_COMMUNICATION")
    if update.callback_query:
        data: str = update.callback_query.data
        page = int(data.split("_")[-1])
        communication_id = data.split("_")[-2]
        communication: AdminMessage = find_admin_message_by_id(communication_id)
        if communication:
            create_admin_message(communication.message)
    else:
        delete_if_private(update.effective_message)
        create_admin_message(update.effective_message.text)
        page = 0
    show_admin_messages(update, context, page)
    return ConversationHandler.END


def cancel_resend_communication(update: Update, context: CallbackContext):
    data: str = update.callback_query.data
    page = int(data.split("_")[-1])
    show_admin_messages(update, context, page)
    return ConversationHandler.END


RESEND_COMMUNICATION_CONVERSATION = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            pattern="ask_resend_communication", callback=ask_resend_communication
        )
    ],
    states={
        RESEND_COMMUNICATION: [
            MessageHandler(Filters.text, resend_commumication),
            CallbackQueryHandler(
                pattern="resend_communication", callback=resend_commumication
            ),
        ]
    },
    fallbacks=[
        CallbackQueryHandler(
            cancel_resend_communication, pattern="conv_view_admin_comms"
        ),
    ],
)