#!/usr/bin/env python3

""" Docstring """

from root.helper.redis_message import add_message
from root.manager.start import back_to_the_start
from telegram import Update, Message, InlineKeyboardMarkup, CallbackQuery, User
from telegram.ext import CallbackContext
from telegram.error import BadRequest
from root.util.telegram import TelegramSender
from root.util.util import append_timeout_message, create_button, retrieve_key
from root.contants.messages import (
    HOW_TO_PAGES,
    HOW_TO_DEEP_LINK,
)
from root.helper.process_helper import create_process, stop_process
from root.contants.message_timeout import ONE_MINUTE, FIVE_MINUTES

sender = TelegramSender()


def help_init(update: Update, context: CallbackContext):
    """Initialize the help session with the user

    Args:
        update (Update): Telegram update
        context (CallbackContext): The context of the telegram bot
    """
    add_message(update.effective_message.message_id, update.effective_user.id)
    bot_help(update, context, page=0)


def help_navigate(update: Update, context: CallbackContext):
    """Navigate in the various pages of the help section

    Args:
        update (Update): Telegram update
        context (CallbackContext): The context of the telegram bot
    """
    context.bot.answer_callback_query(update.callback_query.id)
    callback: CallbackQuery = update.callback_query
    query: str = callback.data
    page: int = int(query.split("_")[-1])
    bot_help(update, context, page, True)


def send_redirect(update: Update, context: CallbackContext) -> None:
    """When is summoned

    Args:
        update (Update): Telegram update
        context (CallbackContext): The context of the telegram bot
    """
    bot_name = retrieve_key("BOT_NAME")
    user: User = update.effective_user
    user_id: int = user.id
    chat_id: int = update.effective_chat.id
    first_name: str = user.first_name
    message = HOW_TO_DEEP_LINK % (user_id, first_name, bot_name)
    button = create_button(
        message="📚  Apri la guida completa",
        callback="help_redirect",
        query="help_redirect",
        url=f"t.me/{bot_name}?start=how_to",
    )
    sender.send_and_delete(
        update.effective_message.message_id,
        update.effective_user.id,
        context,
        chat_id,
        message,
        reply_markup=InlineKeyboardMarkup([[button]]),
        timeout=ONE_MINUTE,
    )


def bot_help(
    update: Update, context: CallbackContext, page: int = 0, edit: bool = False
):
    """Generic method to handle the help session

    Args:
        update (Update): Telegram update
        context (CallbackContext): The context of the telegram bot
        page (int, optional): The page to view. Defaults to 1.
        edit (bool, optiona): If the message needs to be created or not. Defaults to False.
    """
    message: Message = update.effective_message
    if edit:
        message = update.callback_query.message
    if not sender.check_command(message):
        return
    message_id = message.message_id
    chat_id = message.chat.id
    chat_type = message.chat.type
    if not edit:
        sender.delete_if_private(context, message)
    if not chat_type == "private":
        send_redirect(update, context)
        return
    message, keyboard = create_message(page)
    try:
        stop_process(message_id)
        create_process(
            name_prefix=message_id,
            target=back_to_the_start,
            args=(update, context, chat_id, message_id, FIVE_MINUTES),
        )
        if edit:
            is_private = not update.effective_chat.type == "private"
            if update.effective_chat.type == "private":
                context.bot.answer_callback_query(update.callback_query.id)
                message = append_timeout_message(
                    message, is_private, FIVE_MINUTES, is_private
                )
            context.bot.edit_message_text(
                text=message,
                chat_id=chat_id,
                disable_web_page_preview=True,
                message_id=message_id,
                reply_markup=keyboard,
                parse_mode="HTML",
            )
        else:
            is_private = not update.effective_chat.type == "private"
            message = append_timeout_message(
                message, is_private, FIVE_MINUTES, is_private
            )
            sender.send_and_edit(
                update,
                context,
                chat_id,
                message,
                back_to_the_start,
                keyboard,
                timeout=FIVE_MINUTES,
            )
    except BadRequest:
        return


def create_message(page: int):
    """Build the keyboard for the help message

    Args:
        page (int): The page You want to view
    """
    current_page = HOW_TO_PAGES[page]
    text = current_page["description"]
    keyboards = []
    for index, button in enumerate(HOW_TO_PAGES):
        callback = f"how_to_page_{index}"
        button = button["button_text"]
        if index == page:
            button = f"►     {button}     ◄"
        button = create_button(button, callback, callback)
        keyboards.append([button])
    keyboards.append([create_button("Ho capito!", "how_to_end", "how_to_end")])
    return text, InlineKeyboardMarkup(keyboards)
