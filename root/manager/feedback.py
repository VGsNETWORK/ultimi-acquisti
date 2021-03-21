#!/usr/bin/env python3

""" Feedback manager for  the bot """

from time import sleep
from telegram.ext import (
    ConversationHandler,
    CallbackQueryHandler,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    Filters,
)
from telegram import Update, InlineKeyboardMarkup
from telegram.message import Message
from root.manager.start import conversation_main_menu
from root.util.util import retrieve_key, create_button
from root.contants.messages import FEEDBACK_FROM_MESSAGE, FEEDBACK_SEND_MESSAGE
import root.util.logger as logger
from root.util.telegram import TelegramSender

sender = TelegramSender()

MESSAGE_ID = 0

FEEDBACK_MESSAGE = range(1)

MESSAGE = 0


def start_feedback(update: Update, context: CallbackContext):
    """Start the conversation handler for the feedback

    Args:
        update (Update): Telegram update
        context (CallbackContext): The context of the telegram bot
    """
    global MESSAGE_ID
    if update.callback_query:
        context.bot.answer_callback_query(update.callback_query.id)
    message_id = update.effective_message.message_id
    user_id = update.effective_user.id
    if update.callback_query:
        logger.info("EDITING MESSAGE?????")
        context.bot.edit_message_text(
            text=FEEDBACK_SEND_MESSAGE,
            chat_id=user_id,
            disable_web_page_preview=True,
            message_id=message_id,
            reply_markup=build_keyboard(),
            parse_mode="HTML",
        )
        MESSAGE_ID = message_id
    else:
        message: Message = context.bot.send_message(
            text=FEEDBACK_SEND_MESSAGE,
            chat_id=user_id,
            disable_web_page_preview=True,
            reply_markup=build_keyboard(),
            parse_mode="HTML",
        )
        MESSAGE_ID = message.message_id

    logger.info(message_id)
    return FEEDBACK_MESSAGE


def send_feedback(update: Update, context: CallbackContext):
    """Send the message to the channel after the user typed it

    Args:
        update (Update): Telegram update
        context (CallbackContext): The context of the telegram bot

    """
    chat_id: str = retrieve_key("FEEDBACK_CHANNEL")
    bot_name: str = retrieve_key("BOT_NAME")
    username: str = update.effective_user.username
    user_id: int = update.effective_user.id
    message: str = update.effective_message.text
    if not username:
        username = '<a href="tg://user?id=%s">%s</a>' % (
            user_id,
            update.effective_user.first_name,
        )
    else:
        username = f"@{username}"
    message: str = FEEDBACK_FROM_MESSAGE % (f"{username}", user_id, message)
    message: str = f"{message}\n\n\n#feedback @{bot_name}"
    context.bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")
    conversation_main_menu(update, context, MESSAGE_ID)
    sleep(0.5)
    sender.delete_if_private(context, update.effective_message)
    return ConversationHandler.END


def cancel_feedback(update: Update, context: CallbackContext):
    """Cancel the conversation handler

    Args:
        update (Update): Telegram update
        context (CallbackContext): The context of the telegram bot
    """
    context.bot.answer_callback_query(update.callback_query.id)
    conversation_main_menu(update, context)
    return ConversationHandler.END


def build_keyboard():
    """Create the keyboard for the feedback with the cancel button"""
    return InlineKeyboardMarkup(
        [[create_button("❌  Annulla", "cancel_feedback", "cancel_feedback")]]
    )


FEEDBACK_CONVERSATION = ConversationHandler(
    entry_points=[
        CommandHandler("start", start_feedback, Filters.regex("^.*leave_feedback*.$")),
        CallbackQueryHandler(callback=start_feedback, pattern="send_feedback"),
    ],
    states={FEEDBACK_MESSAGE: [MessageHandler(Filters.text, send_feedback)]},
    fallbacks=[
        CallbackQueryHandler(callback=cancel_feedback, pattern="cancel_feedback")
    ],
)
