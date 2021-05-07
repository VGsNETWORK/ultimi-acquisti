#!/usr/bin/env python3

""" File to handle the start command """

from os import environ
import re

from mongoengine.errors import DoesNotExist
from root.model.configuration import Configuration

from mongoengine.fields import key_not_string

from root.helper.process_helper import stop_process
from time import sleep
from datetime import datetime
from telegram import Update, Message, User, InlineKeyboardMarkup, CallbackQuery, message
from telegram.bot import Bot
from telegram.ext import CallbackContext
from root.util.telegram import TelegramSender
from root.util.util import create_button, retrieve_key
from root.contants.messages import (
    START_COMMAND,
    START_COMMANDS_LIST,
    PLEASE_NOTE_APPEND,
    START_COMMANDS_LIST_HEADER,
    START_GROUP_GROUP_APPEND,
)
from root.helper.redis_message import add_message
from root.contants.message_timeout import THREE_MINUTES
import root.util.logger as logger
from root.contants.VERSION import VERSION
from root.model.user_rating import UserRating

DEVELOPER = '<a href="https://t.me/WMD_Edoardo">Edoardo Zerbo</a>'
DESIGNER = '<a href="https://t.me/WMD_Lorenzo">Lorenzo Maffii</a>'

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
        context.bot.send_message(
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
    update: Update,
    _: CallbackContext,
    message_id: int = None,
    original_message: Message = None,
):
    """Show the main menu after a conversation handler

    Args:
        update (Update): Telegram update
        context (CallbackContext): The context of the telegram bot
    """
    logger.info("Received main_menu")
    logger.info(f"THIS IS THE MESSAGE_ID: {message_id}")
    if update:
        message: Message = update.effective_message
        logger.info("retrieving the message_id")
        message_id = message_id if message_id else message.message_id
        chat_id = message.chat.id
    else:
        chat_id: int = original_message.chat.id
        logger.info("No update, callback from mtproto")
    logger.info(f"Message is {message_id}, editing message on chat {chat_id}")
    if update:
        user = update.effective_user
    else:
        user = original_message.from_user
        message = original_message
    try:
        bot = Bot(environ["TOKEN"])
        bot.edit_message_text(
            text=build_message(user, message),
            chat_id=chat_id,
            disable_web_page_preview=True,
            reply_markup=build_keyboard(message),
            message_id=message_id,
            parse_mode="HTML",
            timeout=10,
        )
    except Exception as e:
        logger.exception(e)


def append_commands(update: Update, context: CallbackContext, page: int = 0):
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
    max_pages = len(START_COMMANDS_LIST)
    keyboard = InlineKeyboardMarkup(
        [
            [
                create_button(
                    "◄" if page > 0 else "🔚",
                    f"command_page_{page - 1}" if page > 0 else "empty_button",
                    f"command_page_{page - 1}" if page > 0 else "empty_button",
                ),
                create_button(
                    f"{page + 1}/{max_pages}",
                    "empty_button",
                    "empty_button",
                ),
                create_button(
                    "►" if page + 1 < max_pages else "🔚",
                    f"command_page_{page + 1}"
                    if page + 1 < max_pages
                    else "empty_button",
                    f"command_page_{page + 1}"
                    if page + 1 < max_pages
                    else "empty_button",
                ),
            ],
            [
                create_button(
                    "🔺     Nascondi i comandi     🔺",
                    "start_hide_commands",
                    "start_hide_commands",
                ),
            ],
            [create_button("📚  Guida", "how_to_page_0", "how_to_page_0")],
            [
                create_button(
                    "📈  Apri il report mensile", "expand_report", "expand_report"
                ),
                create_button(
                    "📈  Apri il report annuale",
                    f"expand_year_report_{current_year}",
                    f"expand_year_report_{current_year}",
                ),
            ],
            [
                create_button(
                    "ℹ️  Info",
                    "show_bot_info",
                    "show_bot_info",
                )
            ],
            [
                create_button(
                    "⭐  Valuta il bot",
                    "send_poll",
                    "send_poll",
                )
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
    command = START_COMMANDS_LIST[page]
    message: str = f"{message}\n{START_COMMANDS_LIST_HEADER}{command}"
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


def rating_cancelled(update: Update, context: CallbackContext, message_id):
    answer = update.poll_answer
    poll_id, first_name = answer.poll_id, answer.user.first_name
    user_id = answer.user.id
    poll_data = context.bot_data[poll_id]
    chat_id = poll_data["chat_id"]
    text = f"{START_COMMAND}" % (user_id, first_name, PLEASE_NOTE_APPEND)
    keyboard = InlineKeyboardMarkup(
        [
            [
                create_button(
                    "🔻     Mostra i comandi     🔻",
                    "start_show_commands",
                    "start_show_commands",
                )
            ],
            [create_button("📚  Guida", "how_to_page_0", "how_to_page_0")],
            [
                create_button(
                    "📈  Apri il report mensile", "expand_report", "expand_report"
                ),
                create_button(
                    "📈  Apri il report annuale",
                    f"expand_year_report_{current_year}",
                    f"expand_year_report_{current_year}",
                ),
            ],
            [
                create_button(
                    "ℹ️  Info",
                    "show_bot_info",
                    "show_bot_info",
                )
            ],
            [
                create_button(
                    "⭐  Valuta il bot",
                    "send_poll",
                    "send_poll",
                )
            ],
            [
                create_button(
                    "🆘  Supporto",
                    "send_feedback",
                    "send_feedback",
                )
            ],
        ]
    )
    context.bot.edit_message_text(
        message_id=message_id,
        chat_id=chat_id,
        text=text,
        reply_markup=keyboard,
        disable_web_page_preview=True,
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
                [create_button("📚  Guida", "how_to_page_0", "how_to_page_0")],
                [
                    create_button(
                        "📈  Apri il report mensile", "expand_report", "expand_report"
                    ),
                    create_button(
                        "📈  Apri il report annuale",
                        f"expand_year_report_{current_year}",
                        f"expand_year_report_{current_year}",
                    ),
                ],
                [
                    create_button(
                        "ℹ️  Info",
                        "show_bot_info",
                        "show_bot_info",
                    )
                ],
                [
                    create_button(
                        "⭐  Valuta il bot",
                        "send_poll",
                        "send_poll",
                    )
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


def navigate_command_list(update: Update, _: CallbackContext):
    global COMMAND_MESSAGE
    callback: CallbackQuery = update.callback_query
    page: str = callback.data
    page = page.split("_")[-1]
    if not page.isdigit():
        return
    page = int(page)
    append_commands(update, callback, page)


def back_to_the_start(
    update: Update,
    context: CallbackContext,
    _: int,
    message_id: int,
    timeout: int = 0,
    original_message: Message = None,
):
    logger.info("Waiting for the process to end...")
    sleep(timeout)
    logger.info("Running the main_menu")
    conversation_main_menu(update, context, message_id, original_message)


def show_info(update: Update, context: CallbackContext):
    message = update.effective_message
    message_id = message.message_id
    chat = update.effective_chat
    try:
        average_rating: Configuration = Configuration.objects.get(code="average_rating")
        average = average_rating.value
    except DoesNotExist as _:
        average = ""
    keyboard = InlineKeyboardMarkup(
        [[create_button("↩️  Torna indietro", "how_to_end", "how_to_end")]]
    )
    number_of_reviews = len(UserRating.objects().filter(approved=True))
    average_message = int(float(average)) * "🌕" if average else ""
    average_message += f"{(5 - len(average_message)) * '🌑'}"
    logger.info(average_message)
    index = int(average.split(".")[0])
    decimal = average.split(".")[1][0:2]
    if len(decimal) < 2:
        decimal += "0"
    decimal = int(decimal)
    logger.info(decimal)
    if decimal != 0:
        if decimal >= 75:
            replace = "🌖"
        if decimal < 75:
            replace = "🌗"
        if decimal < 50:
            replace = "🌘"
        if decimal < 25:
            replace = "🌑"
        average_message = [c for c in average_message]
        average_message[index] = replace
        average_message = "".join(average_message)

    average_message = (
        f"🌐  Valutazione:\n        <b>{'%.2f' % (float(average))}</b>  {average_message}  (basato su {number_of_reviews} recensioni)\n\n"
        if average_message
        else ""
    )
    message = (
        f"<u><b>INFO</b></u>\n\n\n"
        f"{average_message}"
        f"🔄  Versione:  <code>{VERSION}</code>\n\n"
        f"☕️  Sviluppatore:  {DEVELOPER}\n"
        f"🎨  UX/UI Designer:  {DESIGNER}\n\n\n"
        f"<i>A cura di @VGsNETWORK</i>"
    )

    context.bot.edit_message_text(
        chat_id=chat.id,
        text=message,
        reply_markup=keyboard,
        message_id=message_id,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
