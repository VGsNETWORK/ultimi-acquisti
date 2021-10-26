#!/usr/bin/env python3

from telegram.error import BadRequest
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.ext.conversationhandler import ConversationHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
import telegram_utils.utils.logger as logger
from telegram_utils.utils.tutils import delete_if_private
from root.contants.messages import ADMIN_PANEL_MAIN_MESSAGE, USER_INFO_RECAP_LEGEND
from root.helper.admin_message import create_admin_message
from root.helper.aggregation.user_info import USER_INFO_NATIVE_QUERY
from root.model.user import User
from root.model.wishlist import Wishlist
from root.util.util import create_button
from telegram import Update
from telegram.chat import Chat
from telegram.ext import CallbackContext
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.message import Message
import telegram_utils.helper.redis as redis_helper

SEND_COMMUNICATION = range(1)

ADMIN_PANEL_KEYBOARD = InlineKeyboardMarkup(
    [
        [create_button("✉️  Invia un messaggio", "send_comunication", None)],
        [create_button("📊  Vedi le statistiche", "show_usage", None)],
        [create_button("↩️  Torna indietro", "cancel_rating", None)],
    ]
)

INIT_SEND_COMMUNICATION_KEYBOARD = InlineKeyboardMarkup(
    [[create_button("❌  Annulla", "cancel_send_comunication", None)]]
)


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
    text = "Inserisci la comunicazione:"
    context.bot.edit_message_text(
        chat_id=chat.id,
        message_id=message_id,
        text=text,
        disable_web_page_preview=True,
        reply_markup=INIT_SEND_COMMUNICATION_KEYBOARD,
        parse_mode="HTML",
    )
    return SEND_COMMUNICATION


def send_comunication(update: Update, context: CallbackContext):
    text = update.effective_message.text
    delete_if_private(update.effective_message)
    create_admin_message(text)
    handle_admin(update, context)
    return ConversationHandler.END


SEND_COMUNICATION_CONVERSTATION = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            pattern="send_comunication", callback=init_send_comunication
        )
    ],
    states={SEND_COMMUNICATION: [MessageHandler(Filters.text, send_comunication)]},
    fallbacks=[
        CallbackQueryHandler(handle_admin, pattern="cancel_send_comunication"),
    ],
)