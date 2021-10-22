#!/usr/bin/env python3

""" File to handle the start command """

from os import environ
import re
from root.contants.keyboard import GROUP_START_KEYBOARD
from root.helper.notification import create_notification
from root.manager.command_redirect import command_redirect
from root.helper.user_helper import is_admin

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
    GLOSSARY_LINK,
    REPO_LINK,
    START_COMMAND,
    START_COMMANDS_LIST,
    PLEASE_NOTE_APPEND,
    START_COMMANDS_LIST_HEADER,
    START_GROUP_GROUP_APPEND,
    build_show_notification_button,
)
from root.helper.redis_message import add_message
from root.contants.message_timeout import THREE_MINUTES
import root.util.logger as logger
from root.contants.VERSION import LAST_UPDATE, VERSION
from root.model.user_rating import UserRating

DEVELOPER = '<a href="tg://user?id=84872221">Edoardo Zerbo</a>'
DESIGNER = '<a href="tg://user?id=109191781">Lorenzo Maffii</a>'

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
    if "command_list" in params:
        append_commands(update, context)
    if params == "start":
        message: Message = update.message if update.message else update.edited_message
        chat_id = message.chat.id
        sender.delete_if_private(update, message)
        # TODO: Do I really need this ?
        context.bot.send_message(
            chat_id=chat_id,
            text=build_message(update.effective_user, message),
            reply_markup=build_keyboard(update.effective_user, message),
            parse_mode="HTML",
            disable_web_page_preview=True,
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
    chat_id = message.chat.id
    if message.chat.type == "private":
        msg: Message = context.bot.send_message(
            chat_id=chat_id,
            text=build_message(update.effective_user, message),
            reply_markup=build_keyboard(update.effective_user, message),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
        logger.info(f"FUCK OFF {msg.message_id}")
        add_message(message.message_id, update.effective_user.id)
    else:
        sender.send_and_delete(
            message.message_id,
            update.effective_user.id,
            context,
            chat_id,
            build_message(update.effective_user, message),
            reply_markup=build_keyboard(update.effective_user, message),
            parse_mode="HTML",
            timeout=THREE_MINUTES,
        )
    sender.delete_if_private(update, message)


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
        reply_markup=build_keyboard(update.effective_user, message),
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
            reply_markup=build_keyboard(update.effective_user, message),
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
        try:
            page: int = int(message.text.split("_")[-1])
            page -= 1
        except Exception:
            page = 0
    max_pages = len(START_COMMANDS_LIST)
    if page > max_pages - 1:
        page = max_pages - 1
    elif page < 0:
        page = 0
    if is_admin(update.effective_user.id):
        logger.info("User [%s] is an admin" % update.effective_user.id)
        admin_button = [
            create_button(
                "🎖 PANNELLO ADMIN",
                "show_admin_panel",
                "show_admin_panel",
            ),
            create_button(
                "⚙️  Impostazioni",
                "user_settings",
                "user_settings",
            ),
        ]
    else:
        logger.info("User [%s] is NOT an admin" % update.effective_user.id)
        admin_button = [
            create_button(
                "⚙️  Impostazioni",
                "user_settings",
                "user_settings",
            )
        ]
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
            [create_button("📚  Guida all'utilizzo", "how_to_page_0", "how_to_page_0")],
            [
                create_button(
                    build_show_notification_button(update.effective_user),
                    "show_notifications",
                    "show_notifications",
                )
            ],
            [
                create_button("📈  Report mensile", "expand_report", "expand_report"),
                create_button(
                    "💡 Che cos'è?", "monthly_report_info", "monthly_report_info"
                ),
            ],
            [
                create_button(
                    "📈  Report annuale",
                    f"expand_year_report_{current_year}",
                    f"expand_year_report_{current_year}",
                ),
                create_button(
                    "💡 Che cos'è?", "yearly_report_info", "yearly_report_info"
                ),
            ],
            [
                create_button(
                    "♥️  Lista dei desideri",
                    "view_wishlist_element_0",
                    "view_wishlist_element_0",
                )
            ],
            admin_button,
            [
                create_button(
                    "ℹ️  Info",
                    "show_bot_info",
                    "show_bot_info",
                ),
                create_button(
                    "⭐  Valutami",
                    "rating_menu",
                    "rating_menu",
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
    command = START_COMMANDS_LIST[page]
    message: str = f"{START_COMMANDS_LIST_HEADER}{command}"
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
        reply_markup=build_keyboard(update.effective_user, message),
        parse_mode="HTML",
    )


def rating_cancelled(update: Update, context: CallbackContext, message_id):
    answer = update.poll_answer
    poll_id, first_name = answer.poll_id, answer.user.first_name
    user_id = answer.user.id
    poll_data = context.bot_data[poll_id]
    chat_id = poll_data["chat_id"]
    text = f"{START_COMMAND}" % (user_id, first_name, PLEASE_NOTE_APPEND)
    if is_admin(update.effective_user.id):
        logger.info("User [%s] is an admin" % update.effective_user.id)
        admin_button = [
            create_button(
                "🎖 PANNELLO ADMIN",
                "show_admin_panel",
                "show_admin_panel",
            ),
            create_button(
                "⚙️  Impostazioni",
                "user_settings",
                "user_settings",
            ),
        ]
    else:
        logger.info("User [%s] is NOT an admin" % update.effective_user.id)
        admin_button = [
            create_button(
                "⚙️  Impostazioni",
                "user_settings",
                "user_settings",
            )
        ]
    keyboard = InlineKeyboardMarkup(
        [
            [
                create_button(
                    "🔻     Mostra i comandi     🔻",
                    "start_show_commands",
                    "start_show_commands",
                )
            ],
            [
                create_button(
                    build_show_notification_button(update.effective_user),
                    "show_notifications",
                    "show_notifications",
                )
            ],
            [
                create_button("📈  Report mensile", "expand_report", "expand_report"),
                create_button(
                    "💡 Che cos'è?", "monthly_report_info", "monthly_report_info"
                ),
            ],
            [
                create_button(
                    "📈  Report annuale",
                    f"expand_year_report_{current_year}",
                    f"expand_year_report_{current_year}",
                ),
                create_button(
                    "💡 Che cos'è?", "yearly_report_info", "yearly_report_info"
                ),
            ],
            [
                create_button(
                    "♥️  Lista dei desideri",
                    "view_wishlist_element_0",
                    "view_wishlist_element_0",
                )
            ],
            admin_button,
            [
                create_button(
                    "ℹ️  Info",
                    "show_bot_info",
                    "show_bot_info",
                ),
                create_button(
                    "⭐  Valutami",
                    "rating_menu",
                    "rating_menu",
                ),
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


def build_keyboard(user: User, message: Message) -> InlineKeyboardMarkup:
    """Create a keyboard for the main start menu

    Args:
        message (Message): A Telegram message object

    Returns:
        InlineKeyboardMarkup: A telegram compatible keyboard
    """
    bot_name = retrieve_key("BOT_NAME")
    if message.chat.type == "private":
        if is_admin(user.id):
            logger.info("User [%s] is an admin" % user.id)
            admin_button = [
                create_button(
                    "🎖 PANNELLO ADMIN",
                    "show_admin_panel",
                    "show_admin_panel",
                ),
                create_button(
                    "⚙️  Impostazioni",
                    "user_settings",
                    "user_settings",
                ),
            ]
        else:
            logger.info("User [%s] is NOT an admin" % user.id)
            admin_button = [
                create_button(
                    "⚙️  Impostazioni",
                    "user_settings",
                    "user_settings",
                )
            ]
        return InlineKeyboardMarkup(
            [
                [
                    create_button(
                        "🔻     Mostra i comandi     🔻",
                        "start_show_commands",
                        "start_show_commands",
                    )
                ],
                [
                    create_button(
                        "📚  Guida all'utilizzo", "how_to_page_0", "how_to_page_0"
                    )
                ],
                [
                    create_button(
                        build_show_notification_button(user),
                        "show_notifications",
                        "show_notifications",
                    )
                ],
                [
                    create_button(
                        "📈  Report mensile", "expand_report", "expand_report"
                    ),
                    create_button(
                        "💡 Che cos'è?", "monthly_report_info", "monthly_report_info"
                    ),
                ],
                [
                    create_button(
                        "📈  Report annuale",
                        f"expand_year_report_{current_year}",
                        f"expand_year_report_{current_year}",
                    ),
                    create_button(
                        "💡 Che cos'è?", "yearly_report_info", "yearly_report_info"
                    ),
                ],
                [
                    create_button(
                        "♥️  Lista dei desideri",
                        "view_wishlist_element_0",
                        "view_wishlist_element_0",
                    )
                ],
                admin_button,
                [
                    create_button(
                        "ℹ️  Info",
                        "show_bot_info",
                        "show_bot_info",
                    ),
                    create_button(
                        "⭐  Valutami",
                        "rating_menu",
                        "rating_menu",
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
    return GROUP_START_KEYBOARD


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
    if not update.effective_message.chat.type == "private":
        command_redirect("info", "show_info", update, context)
        return
    spaces = 10
    ux_header = "🤹🏻  <i>Semplicità</i>"
    functionality_header = "➕  <i>Funzionalità</i>"
    ui_header = "👁‍🗨  <i>Interfaccia</i>"
    overall_header = "🌐  <i>Generale</i>"

    message = update.effective_message
    message_id = message.message_id
    chat = update.effective_chat
    try:
        average: Configuration = Configuration.objects.get(code="average_rating").value
        ui_vote: Configuration = Configuration.objects.get(code="ui_vote").value
        ux_vote: Configuration = Configuration.objects.get(code="ux_vote").value
        overall_vote: Configuration = Configuration.objects.get(
            code="overall_vote"
        ).value
        functionality_vote: Configuration = Configuration.objects.get(
            code="functionality_vote"
        ).value
        logger.info(
            f"{average} {ui_vote} {ux_vote} {overall_vote} {functionality_vote}"
        )
    except DoesNotExist as _:
        average, functionality_vote, overall_vote, ui_vote, ux_vote = 0, 0, 0, 0, 0
    keyboard = [
        [
            create_button(
                "⭐  Valutami", "rating_menu_from_info", "rating_menu_from_info"
            )
        ],
        [
            create_button("🔠  Glossario", "glossary_link", None, GLOSSARY_LINK),
            create_button("🐙  Link al progetto", "github_link", None, REPO_LINK),
        ],
        [create_button("↩️  Torna indietro", "how_to_end", "how_to_end")],
    ]
    number_of_reviews = len(UserRating.objects().filter(approved=True))
    average_message = create_rating_moons(average)
    average_header = ux_header
    hlength = len(average_header)
    message = f"<u><b>INFO</b></u>\n\n\n"

    callback = update.callback_query

    if callback:
        data = callback.data
    else:
        data = "do_not_expand"
    if data == "expand_info":
        button = [
            create_button(
                "🔺     Comprimi valutazione     🔺", "show_bot_info", "show_bot_info"
            )
        ]
        keyboard.insert(0, button)
        message += f"{create_rating_moons(ux_vote)}{' ' * spaces}{ux_header}\n"
        message += f"{create_rating_moons(functionality_vote)}{' ' * spaces}{functionality_header}\n"
        message += f"{create_rating_moons(ui_vote)}{' ' * spaces}{ui_header}\n"
        message += (
            f"{create_rating_moons(overall_vote)}{' ' * spaces}{overall_header}\n"
        )
        # message += f"<code>{'─' * 13}</code>\n"
        message += f"{'─' * 12}\n"
    else:
        button = [
            create_button(
                "🔻     Espandi valutazione     🔻", "expand_info", "expand_info"
            )
        ]
        keyboard.insert(0, button)
    average_header = "⭐️  <i><b>Valutazione</b></i>"
    message += (
        f"{average_message}{' ' * spaces}{average_header}\n" if average_message else ""
    )
    if average_message:
        average_append = f"<i>(basata su {number_of_reviews} recensioni)</i>\n\n\n"
        message += average_append
    message += (
        f"🔄  Versione:  <code>{VERSION}</code>     (rilasciata il {LAST_UPDATE})\n\n"
    )
    message += f"☕️  Sviluppatore:  {DEVELOPER}\n"
    message += f"🎨  UX/UI Designer:  {DESIGNER}\n\n\n"
    message += f"<i>A cura di @VGsNETWORK</i>"
    if callback:
        context.bot.edit_message_text(
            chat_id=chat.id,
            text=message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            message_id=message_id,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    else:
        sender.delete_if_private(context, update.effective_message)
        context.bot.send_message(
            chat_id=chat.id,
            text=message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )


def create_rating_moons(average):
    logger.info(f"creating message for {average}")
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
        logger.info(average_message)
        average_message = [c for c in average_message]
        logger.info(average_message)
        average_message[index] = replace
        logger.info(average_message)
    message = "".join(average_message)
    return f"<b>{'%.2f' % (float(average))}</b>   {message}"