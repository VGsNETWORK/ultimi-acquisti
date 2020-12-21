#!/usr/bin/env python3

""" Feedback manager for  the bot """

from telegram.ext import (
    ConversationHandler,
    CallbackQueryHandler,
    CallbackContext,
    MessageHandler,
    Filters,
)
from telegram import Update, InlineKeyboardMarkup
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
    context.bot.answer_callback_query(update.callback_query.id)
    message_id = update.effective_message.message_id
    user_id = update.effective_user.id
    context.bot.edit_message_text(
        text=FEEDBACK_SEND_MESSAGE,
        chat_id=user_id,
        disable_web_page_preview=True,
        message_id=message_id,
        reply_markup=build_keyboard(),
        parse_mode="HTML",
    )
    MESSAGE_ID = message_id
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
    message: str = FEEDBACK_FROM_MESSAGE % (f"@{username}", user_id, message)
    message: str = f"{message}\n\n\n#feedback @{bot_name}"
    context.bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")
    sender.delete_if_private(context, update.effective_message)
    conversation_main_menu(update, context, MESSAGE_ID)
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
        CallbackQueryHandler(callback=start_feedback, pattern="send_feedback")
    ],
    states={FEEDBACK_MESSAGE: [MessageHandler(Filters.text, send_feedback)]},
    fallbacks=[
        CallbackQueryHandler(callback=cancel_feedback, pattern="cancel_feedback")
    ],
)
