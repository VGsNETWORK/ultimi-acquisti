#!/usr/bin/env python3

from os import link
from subprocess import call
from root.contants.messages import (
    ADDED_TO_WISHLIST,
    ADD_LINK_TO_WISHLIST_ITEM_MESSAGE,
    ADD_TO_WISHLIST_PROMPT,
    NO_ELEMENT_IN_WISHLIST,
    WISHLIST_DESCRIPTION_TOO_LONG,
)
from root.util.util import (
    create_button,
    extract_first_link_from_message,
    max_length_error_format,
)
from root.helper.wishlist import (
    find_wishlist_for_user,
    get_total_wishlist_pages_for_user,
    remove_wishlist_item_for_user,
)
from typing import List
from root.model.wishlist import Wishlist
from root.contants.keyboard import (
    ADDED_TO_WISHLIST_KEYBOARD,
    ADD_LINK_TO_WISHLIST_ITEM,
    ADD_TO_WISHLIST_ABORT_KEYBOARD,
    create_wishlist_keyboard,
)
from telegram import Update
from telegram.chat import Chat
from telegram.error import BadRequest
from telegram.ext import CallbackContext
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.ext.conversationhandler import ConversationHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram.message import Message
from telegram.user import User
import telegram_utils.helper.redis as redis_helper
import telegram_utils.utils.logger as logger

INSERT_ITEM_IN_WISHLIST, INSERT_ZELDA = range(2)


def remove_wishlist_item(update: Update, context: CallbackContext):
    user: User = update.effective_user
    if update.callback_query:
        context.bot.answer_callback_query(update.callback_query.id)
        _id = update.callback_query.data.split("_")[-1]
        page = int(update.callback_query.data.split("_")[-2])
        remove_wishlist_item_for_user(_id)
        total_pages = get_total_wishlist_pages_for_user(user.id)
        if page + 1 > total_pages:
            page -= 1
        update.callback_query.data += "_%s" % page
    view_wishlist(update, context)


def view_wishlist(
    update: Update, context: CallbackContext, append: str = None, page: int = None
):
    message: Message = update.effective_message
    message_id = message.message_id
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    if update.callback_query:
        context.bot.answer_callback_query(update.callback_query.id)
    if not page:
        page = int(update.callback_query.data.split("_")[-1])
    else:
        page = int(page)
        message_id = redis_helper.retrieve(user.id).decode()
    total_pages = get_total_wishlist_pages_for_user(user.id)
    wishlists = find_wishlist_for_user(user.id, page)

    chat: Chat = update.effective_chat
    if chat.type != "private":
        # ignore all requests coming outside a private chat
        return
    if wishlists:
        [logger.info(wish.link) for wish in wishlists]
        [logger.info(1 if wish.link else 0) for wish in wishlists]
        message = "\n".join(
            [
                (
                    f'<b>{(index) + (5 * page + 1)}.</b>  <a href="{wish.link}">{wish.description}</a>\n'
                    f"<i>Aggiunto il {wish.creation_date.strftime('%d/%m/%Y')}</i>\n"
                    if wish.link
                    else f"<b>{(index) + (5 * page + 1)}.</b>  {wish.description}\n"
                    f"<i>Aggiunto il {wish.creation_date.strftime('%d/%m/%Y')}</i>\n"
                )
                for index, wish in enumerate(wishlists)
            ]
        )
    else:
        message = NO_ELEMENT_IN_WISHLIST
    message = "<b><u>LISTA DEI DESIDERI</u></b>\n\n\n%s" % message
    first_page = page + 1 == 1
    last_page = page + 1 == total_pages
    if append:
        message += "\n\n%s" % append
    context.bot.edit_message_text(
        chat_id=chat.id,
        message_id=message_id,
        text=message,
        reply_markup=create_wishlist_keyboard(
            page, total_pages, wishlists, first_page, last_page
        ),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


def add_in_wishlist(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    user: User = update.effective_user
    message_id = message.message_id
    if update.callback_query:
        context.bot.answer_callback_query(update.callback_query.id)
    chat: Chat = update.effective_chat
    if chat.type != "private":
        # ignore all requests coming outside a private chat
        return ConversationHandler.END
    redis_helper.save(user.id, message.message_id)
    wishlists = find_wishlist_for_user(user.id, page_size=4)
    message = (
        "<b><u>LISTA DEI DESIDERI</u></b>\n\n\n<b>1.</b>  . . . . . .\n"
        "✍🏻  <i>Stai inserendo questo elemento</i>\n\n"
    )
    if wishlists:
        message += "\n".join(
            [
                (
                    f'<b>{index + 2}.</b>  <a href="{wish.link}">{wish.description}</a>\n'
                    f"<i>Aggiunto il {wish.creation_date.strftime('%d/%m/%Y')}</i>\n"
                    if wish.link
                    else f"<b>{index + 2}.</b>  {wish.description}\n"
                    f"<i>Aggiunto il {wish.creation_date.strftime('%d/%m/%Y')}</i>\n"
                )
                for index, wish in enumerate(wishlists)
            ]
        )
        message += "\n\n%s" % ADD_TO_WISHLIST_PROMPT
    else:
        message += "\n%s" % ADD_TO_WISHLIST_PROMPT
    print(message)
    context.bot.edit_message_text(
        chat_id=chat.id,
        message_id=message_id,
        text=message,
        reply_markup=ADD_TO_WISHLIST_ABORT_KEYBOARD,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
    return INSERT_ITEM_IN_WISHLIST


def handle_add_confirm(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    message_id: int = message.message_id
    message = message.text if message.text else message.caption
    user: User = update.effective_user
    chat: Chat = update.effective_chat
    if chat.type != "private":
        # ignore all requests coming outside a private chat
        return ConversationHandler.END
    # delete the user message
    context.bot.delete_message(chat_id=chat.id, message_id=message_id)
    overload = False
    message_id = redis_helper.retrieve(user.id).decode()
    if len(message) > 128:
        overload = True
        wishlists = find_wishlist_for_user(user.id, page_size=4)
        user_text = max_length_error_format(update.effective_message.text, 128, 200)
        message = (
            f"<b><u>LISTA DEI DESIDERI</u></b>\n\n\n<b>1.</b>  {user_text}\n"
            f"{WISHLIST_DESCRIPTION_TOO_LONG}"
        )
        if wishlists:
            message += "\n".join(
                [
                    (
                        f'<b>{index + 2}.</b>  <a href="{wish.link}">{wish.description}</a>\n'
                        f"<i>Aggiunto il {wish.creation_date.strftime('%d/%m/%Y')}</i>\n"
                        if wish.link
                        else f"<b>{index + 2}.</b>  {wish.description}\n"
                        f"<i>Aggiunto il {wish.creation_date.strftime('%d/%m/%Y')}</i>\n"
                    )
                    for index, wish in enumerate(wishlists)
                ]
            )
            message += "\n\n%s" % ADD_TO_WISHLIST_PROMPT
        else:
            message += "\n%s" % ADD_TO_WISHLIST_PROMPT
        keyboard = ADD_TO_WISHLIST_ABORT_KEYBOARD
        try:
            context.bot.edit_message_text(
                chat_id=chat.id,
                text=message,
                message_id=message_id,
                reply_markup=keyboard,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
        except BadRequest:
            pass
    else:
        Wishlist(user_id=user.id, description=message).save()
        context.bot.edit_message_text(
            message_id=message_id,
            chat_id=chat.id,
            text=ADD_LINK_TO_WISHLIST_ITEM_MESSAGE,
            reply_markup=ADD_LINK_TO_WISHLIST_ITEM,
        )
    return INSERT_ZELDA if not overload else INSERT_ITEM_IN_WISHLIST


def cancel_add_in_wishlist(update: Update, context: CallbackContext):
    update.callback_query.data += "_0"
    view_wishlist(update, context)
    return ConversationHandler.END


def handle_insert_for_link(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    chat: Chat = update.effective_chat
    message_id = message.message_id
    user = update.effective_user
    if not update.callback_query:
        context.bot.delete_message(chat_id=chat.id, message_id=message.message_id)
        wishlist: Wishlist = find_wishlist_for_user(user.id, 0, 1)
        if wishlist:
            wishlist = wishlist[0]
            wishlist.link = message.text if message.text else message.caption
            wishlist.link = extract_first_link_from_message(update.effective_message)
            logger.info(wishlist.link)
            wishlist.save()
    view_wishlist(update, context, ADDED_TO_WISHLIST, "0")
    return ConversationHandler.END


ADD_IN_WISHLIST_CONVERSATION = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(add_in_wishlist, pattern="add_to_wishlist"),
    ],
    states={
        INSERT_ITEM_IN_WISHLIST: [
            MessageHandler(Filters.text, handle_add_confirm),
        ],
        INSERT_ZELDA: [
            MessageHandler(Filters.entity("url"), handle_insert_for_link),
            CallbackQueryHandler(
                callback=handle_insert_for_link, pattern="skip_add_link_to_wishlist"
            ),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(cancel_add_in_wishlist, pattern="cancel_add_to_wishlist"),
    ],
)