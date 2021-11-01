#!/usr/bin/env python3

""" Feedback manager for  the bot """

from time import sleep
from telegram.chat import Chat
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
from telegram_utils.utils.tutils import delete_if_private
from root.contants import keyboard
from root.manager.start import conversation_main_menu
from root.util.util import retrieve_key, create_button
from root.contants.messages import (
    FEEDBACK_CATEGORIES,
    FEEDBACK_CATEGORIES_BUTTONS,
    FEEDBACK_CHOOSE_CATEGORY,
    FEEDBACK_FROM_MESSAGE,
    FEEDBACK_SEND_MESSAGE,
    NEW_FEEDBACK_SENT,
)
import root.util.logger as logger
from root.util.telegram import TelegramSender
from telegram_utils.helper import redis as redis_helper

sender = TelegramSender()

MESSAGE_ID = 0

FEEDBACK_CATEGORY, FEEDBACK_MESSAGE = range(2)

MESSAGE = 0


def start_feedback(update: Update, context: CallbackContext):
    global MESSAGE_ID
    keyboard = []
    redis_helper.save("%s_feedback_category" % update.effective_user.id, "0")
    for button_line in FEEDBACK_CATEGORIES_BUTTONS:
        line = []
        for button in button_line:
            callback = "select_category_%s" % FEEDBACK_CATEGORIES.index(button)
            line.append(create_button(button, callback, None))
        keyboard.append(line)
    keyboard.append([create_button("❌  Annulla", "cancel_feedback", None)])
    keyboard = InlineKeyboardMarkup(keyboard)
    message = FEEDBACK_CHOOSE_CATEGORY
    MESSAGE_ID = update.effective_message.message_id
    context.bot.edit_message_text(
        text=message,
        chat_id=update.effective_user.id,
        disable_web_page_preview=True,
        message_id=update.effective_message.message_id,
        reply_markup=keyboard,
        parse_mode="HTML",
    )
    return FEEDBACK_CATEGORY


def ask_for_message(update: Update, context: CallbackContext):
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
    category_index = redis_helper.retrieve(
        "%s_feedback_category" % update.effective_user.id
    ).decode()
    category_index = int(category_index)
    category = FEEDBACK_CATEGORIES[category_index]
    if update.callback_query:
        context.bot.edit_message_text(
            text=FEEDBACK_SEND_MESSAGE % category.upper(),
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
    category_index = redis_helper.retrieve(
        "%s_feedback_category" % update.effective_user.id
    ).decode()
    delete_if_private(update.effective_message)
    category_index = int(category_index)
    category = FEEDBACK_CATEGORIES[category_index]
    logger.info("THIS IS THE CATEGORY %s" % category)
    if not username:
        username = '<a href="tg://user?id=%s">%s</a>' % (
            user_id,
            update.effective_user.first_name,
        )
    else:
        username = f"@{username}"
    message: str = FEEDBACK_FROM_MESSAGE % (category, f"{username}", user_id, message)
    message: str = f"{message}\n\n\n#feedback @{bot_name}"
    context.bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")
    logger.info("THIS IS THE APPEND [%s]" % NEW_FEEDBACK_SENT)
    conversation_main_menu(update, context, MESSAGE_ID, append=NEW_FEEDBACK_SENT)
    sleep(0.5)
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


def select_category(update: Update, context: CallbackContext):
    logger.info("CATEGORY SELECT")
    data = update.callback_query.data
    message: Message = update.effective_chat
    chat: Chat = update.effective_chat
    category_index = int(data.split("_")[-1])
    logger.info("THIS IS THE CATEGORY %s" % category_index)
    redis_helper.save("%s_feedback_category" % update.effective_user.id, category_index)
    ask_for_message(update, context)
    return FEEDBACK_MESSAGE


FEEDBACK_CONVERSATION = ConversationHandler(
    entry_points=[
        CommandHandler("start", start_feedback, Filters.regex("^.*leave_feedback*.$")),
        CallbackQueryHandler(callback=start_feedback, pattern="send_feedback"),
    ],
    states={
        FEEDBACK_CATEGORY: [
            CallbackQueryHandler(
                callback=select_category,
                pattern="select_category",
            )
        ],
        FEEDBACK_MESSAGE: [MessageHandler(Filters.text, send_feedback)],
    },
    fallbacks=[
        CallbackQueryHandler(callback=cancel_feedback, pattern="cancel_feedback")
    ],
)
