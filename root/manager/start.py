#!/usr/bin/env python3

""" File to handle the start command """

import re
from telegram import Update, Message, User, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import CallbackContext
from root.manager.help import bot_help
from root.util.telegram import TelegramSender
from root.util.util import create_button, retrieve_key
from root.contants.messages import START_COMMAND, NOT_ALLOWED_IN_GROUP
from root.helper.process_helper import restart_process
from root.contants.message_timeout import LONG_SERVICE_TIMEOUT, MONTH_REPORT_TIMEOUT

sender = TelegramSender()


def handle_params(update: Update, context: CallbackContext, params: str) -> None:
    """handle various params recevied during the /start command

    Args:
        update (Update): Telegram update
        context (CallbackContext): The context of the telegram bot
        params (str): the params passed to the /start command
    """
    params = params.rstrip().lstrip()
    if params == "how_to":
        bot_help(update, context)
    if params == "start":
        message: Message = update.message if update.message else update.edited_message
        chat_id = message.chat.id
        sender.delete_if_private(update, message)
        sender.send_and_delete(
            context,
            chat_id,
            build_message(message),
            reply_markup=build_keyboard(message),
        )
    return


def handle_start(update: Update, context: CallbackContext) -> None:
    """Handle the command /start from the user along with some query params

    Args:
        update (Update): Telegram update
        context (CallbackContext): The context of the telegram bot
    """
    message: Message = update.message if update.message else update.edited_message
    params = message.text.replace("/start", "")
    params = re.sub(r"\/\w+\s", "", params)
    if params:
        handle_params(update, context, params)
        return
    sender.delete_if_private(update, message)
    chat_id = message.chat.id
    sender.send_and_delete(
        context,
        chat_id,
        build_message(update.effective_user, message),
        reply_markup=build_keyboard(message),
        timeout=get_timeout(message),
    )


def help_end(update: Update, context: CallbackContext):
    """End the help session with the user

    Args:
        update (Update): Telegram update
        context (CallbackContext): The context of the telegram bot
    """
    context.bot.answer_callback_query(update.callback_query.id)
    callback: CallbackQuery = update.callback_query
    message: Message = callback.message
    restart_process(message.message_id, timeout=get_timeout(message))
    context.bot.edit_message_text(
        text=build_message(update.effective_user, message),
        chat_id=message.chat.id,
        disable_web_page_preview=True,
        message_id=message.message_id,
        reply_markup=build_keyboard(message),
        parse_mode="HTML",
    )


def get_timeout(message: Message) -> int:
    if message.chat.type != "private":
        return LONG_SERVICE_TIMEOUT
    return MONTH_REPORT_TIMEOUT


def build_message(user: User, message: Message) -> str:
    """Create the message to show with the start menu

    Args:
        message (Message): A Telegram message object

    Returns:
        str: The formatted message
    """
    user_id: int = user.id
    first_name: str = user.first_name
    if message.chat.type == "private":
        message = START_COMMAND
    else:
        message = NOT_ALLOWED_IN_GROUP
    return message % (user_id, first_name)


def build_keyboard(message: Message) -> InlineKeyboardMarkup:
    """Create a keyboard for the main start menu

    Args:
        message (Message): A Telegram message object

    Returns:
        InlineKeyboardMarkup: A telegram compatible keyboard
    """
    bot_name = retrieve_key("BOT_NAME")
    if message.chat.type == "private":
        return InlineKeyboardMarkup(
            [[create_button("📜  Guida", "how_to_page_1", "how_to_page_1")]]
        )
    return InlineKeyboardMarkup(
        [
            [
                create_button(
                    "↩️  Privata",
                    "go_start",
                    "go_start",
                    url=f"t.me/{bot_name}?start=start",
                )
            ]
        ]
    )
