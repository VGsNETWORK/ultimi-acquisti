#!/usr/bin/env python3

""" File to handle the start command """

from os import environ
import re
from root.helper.process_helper import stop_process
from time import sleep
from datetime import datetime
from telegram import Update, Message, User, InlineKeyboardMarkup, CallbackQuery
from telegram.bot import Bot
from telegram.ext import CallbackContext
from root.util.telegram import TelegramSender
from root.util.util import create_button, format_error, retrieve_key
from root.contants.messages import (
    START_COMMAND,
    START_COMMANDS_LIST,
    PLEASE_NOTE_APPEND,
    START_GROUP_GROUP_APPEND,
)
from root.contants.message_timeout import TWO_MINUTES, FIVE_MINUTES
from root.helper.redis_message import add_message
from root.contants.message_timeout import THREE_MINUTES
from root.helper.redis_message import message_exist
import root.util.logger as logger

sender = TelegramSender()
current_year = datetime.now().year


def handle_params(update: Update, context: CallbackContext, params: str) -> None:
    """handle various params recevied during the /start command

    Args:
        update (Update): Telegram update
        context (CallbackContext): The context of the telegram bot
        params (str): the params passed to the /start command
    """
    params = params.rstrip().lstrip()
    if params == "command_list":
        append_commands(update, context)
    if params == "start":
        message: Message = update.message if update.message else update.edited_message
        chat_id = message.chat.id
        sender.delete_if_private(update, message)
        # TODO: Do I really need this ?
        msg: Message = context.bot.send_message(
            chat_id=chat_id,
            text=build_message(update.effective_user, message),
            reply_markup=build_keyboard(message),
            parse_mode="HTML",
        )
        add_message(message.message_id, update.effective_user.id)
    return


def handle_start(update: Update, context: CallbackContext) -> None:
    """Handle the command /start from the user along with some query params

    Args:
        update (Update): Telegram update
        context (CallbackContext): The context of the telegram bot
    """
    bot_name: str = retrieve_key("BOT_NAME")
    bot_name = f"/start@{bot_name}"
    message: Message = update.message if update.message else update.edited_message
    logger.info("private message with message_id: %s" % message.message_id)
    if not bot_name in message.text and message.chat.type != "private":
        return
    params = re.sub(f"{bot_name}|/start", "", message.text)
    params = re.sub(r"\/\w+\s", "", params)
    if params:
        handle_params(update, context, params)
        return
    sender.delete_if_private(update, message)
    chat_id = message.chat.id
    if message.chat.type == "private":
        msg: Message = context.bot.send_message(
            chat_id=chat_id,
            text=build_message(update.effective_user, message),
            reply_markup=build_keyboard(message),
            parse_mode="HTML",
        )
        logger.info(f"FUCK OFF {msg.message_id}")
        add_message(message.message_id, update.effective_user.id)
    else:
        sender.send_and_delete(
            message.message_id,
            message.from_user.id,
            context,
            chat_id,
            build_message(update.effective_user, message),
            reply_markup=build_keyboard(message),
            parse_mode="HTML",
            timeout=THREE_MINUTES,
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
    message_id = message.message_id
    stop_process(message_id)
    context.bot.edit_message_text(
        text=build_message(update.effective_user, message),
        chat_id=message.chat.id,
        disable_web_page_preview=True,
        message_id=message_id,
        reply_markup=build_keyboard(message),
        parse_mode="HTML",
    )


def conversation_main_menu(
    update: Update, context: CallbackContext, message_id: int = None
):
    """Show the main menu after a conversation handler

    Args:
        update (Update): Telegram update
        context (CallbackContext): The context of the telegram bot
    """
    logger.info("Received main_menu")
    message: Message = update.effective_message
    logger.info("retrieving the message_id")
    message_id = message_id if message_id else message.message_id
    chat_id = message.chat.id
    logger.info(f"Message is {message_id}, editing message on chat {chat_id}")
    try:
        bot = Bot(environ["TOKEN"])
        bot.edit_message_text(
            text=build_message(update.effective_user, message),
            chat_id=chat_id,
            disable_web_page_preview=True,
            reply_markup=build_keyboard(message),
            message_id=message_id,
            parse_mode="HTML",
            timeout=10,
        )
    except Exception as e:
        logger.exception(e)


def append_commands(update: Update, context: CallbackContext):
    """Append the list of commands to the start message

    Args:
        update (Update): Telegram update
        context (CallbackContext): The context of the telegram bot
    """
    if update.callback_query:
        callback: CallbackQuery = update.callback_query
        message: Message = callback.message
    else:
        message: Message = update.effective_message
    keyboard = InlineKeyboardMarkup(
        [
            [
                create_button(
                    "🔺     Nascondi i comandi     🔺",
                    "start_hide_commands",
                    "start_hide_commands",
                )
            ],
            [create_button("ℹ️  Guida", "how_to_page_1", "how_to_page_1")],
            [
                create_button(
                    "💳  Apri il report mensile", "expand_report", "expand_report"
                ),
                create_button(
                    "💳  Apri il report annuale",
                    f"expand_year_report_{current_year}",
                    f"expand_year_report_{current_year}",
                ),
            ],
            [
                create_button(
                    "🆘  Supporto",
                    "send_feedback",
                    "send_feedback",
                    # url="t.me/VGsNETWORK_Bot?start=leave_feedback",
                )
            ],
        ]
    )
    chat_id: int = message.chat.id
    message_id: int = message.message_id
    message: str = build_message(update.effective_user, message)
    message: str = f"{message}\n{START_COMMANDS_LIST}"
    if update.callback_query:
        context.bot.edit_message_text(
            text=message,
            chat_id=chat_id,
            disable_web_page_preview=True,
            message_id=message_id,
            reply_markup=keyboard,
            parse_mode="HTML",
        )
    else:
        msg: Message = context.bot.send_message(
            text=message,
            chat_id=chat_id,
            disable_web_page_preview=True,
            reply_markup=keyboard,
            parse_mode="HTML",
        )
        logger.info(f"FUCK OFF {msg.message_id}")


def remove_commands(update: Update, context: CallbackContext):
    """Remove the list of commands to the start message

    Args:
        update (Update): Telegram update
        context (CallbackContext): The context of the telegram bot
    """
    callback: CallbackQuery = update.callback_query
    message: Message = callback.message
    context.bot.edit_message_text(
        text=build_message(update.effective_user, message),
        chat_id=message.chat.id,
        disable_web_page_preview=True,
        message_id=message.message_id,
        reply_markup=build_keyboard(message),
        parse_mode="HTML",
    )


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
        message = f"{START_COMMAND}" % (user_id, first_name, PLEASE_NOTE_APPEND)
    else:
        message = f"{START_COMMAND}" % (user_id, first_name, START_GROUP_GROUP_APPEND)
    return message


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
            [
                [
                    create_button(
                        "🔻     Mostra i comandi     🔻",
                        "start_show_commands",
                        "start_show_commands",
                    )
                ],
                [create_button("ℹ️  Guida", "how_to_page_1", "how_to_page_1")],
                [
                    create_button(
                        "💳  Apri il report mensile", "expand_report", "expand_report"
                    ),
                    create_button(
                        "💳  Apri il report annuale",
                        f"expand_year_report_{current_year}",
                        f"expand_year_report_{current_year}",
                    ),
                ],
                [
                    create_button(
                        "🆘  Supporto",
                        "send_feedback",
                        "send_feedback",
                        # url="t.me/VGsNETWORK_Bot?start=leave_feedback",
                    )
                ],
            ]
        )
    return InlineKeyboardMarkup(
        [
            [
                create_button(
                    "Maggiori informazioni  ➡️",
                    "go_start",
                    "go_start",
                    url=f"t.me/{bot_name}?start=start",
                )
            ],
        ]
    )


def back_to_the_start(
    update: Update,
    context: CallbackContext,
    chat_id: int,
    message_id: int,
    timeout: int = 0,
):
    logger.info("Waiting for the process to end...")
    sleep(timeout)
    logger.info("Running the main_menu")
    conversation_main_menu(update, context, message_id)
