#!/usr/bin/env python3

from difflib import SequenceMatcher

import telegram_utils.helper.redis as redis_helper
import telegram_utils.utils.logger as logger
from root.contants.keyboard import (
    build_new_link_keyboard,
    build_new_link_keyboard_added,
    view_wishlist_element_links_keyboard,
)
from root.contants.messages import (
    ADD_NEW_LINK_MESSAGE,
    ADD_NEW_LINK_MESSAGE_NUMBER_OF_NEW_LINK,
    SUPPORTED_LINKS_MESSAGE,
    WISHLIST_HEADER,
    WISHLIST_LINK_LIMIT_REACHED,
)
from root.helper import wishlist_element
from root.helper.user_helper import get_current_wishlist_id
from root.helper.wishlist import find_wishlist_by_id
from root.helper.wishlist_element import find_wishlist_element_by_id
from root.model.user import User
from root.model.wishlist import Wishlist
from root.model.wishlist_element import WishlistElement
from telegram.chat import Chat
from telegram.error import BadRequest
from telegram.ext import ConversationHandler
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.message import Message
from telegram.update import Update

APPEND_LINK = range(1)
MAX_LINK_LENGTH = 27
MAX_LINKS_NUMBER = 10


def delete_wishlist_element_link(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    message_id: int = message.message_id
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    if update.callback_query:
        data = update.callback_query.data
        logger.info("THIS IS THE DATA: [%s]" % data)
        wishlist_element_id = data.split("_")[-1]
        page = data.split("_")[-2]
        index = int(data.split("_")[-3])
        wishlist_element: WishlistElement = find_wishlist_element_by_id(
            wishlist_element_id
        )
        links = wishlist_element.links
        links.reverse()
        links.pop(index + 1)
        links.reverse()
        wishlist_element.links = links
        wishlist_element.save()
        view_wishlist_element_links(update, context)
    return


def view_wishlist_element_links(
    update: Update, context: CallbackContext, append: str = None
):
    message: Message = update.effective_message
    message_id: int = message.message_id
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    if update.callback_query:
        data = update.callback_query.data
        wishlist_element_id = data.split("_")[-1]
        page = data.split("_")[-2]
    else:
        info = redis_helper.retrieve(
            "%s_%s_new_link_message" % (user.id, user.id)
        ).decode()
        page = info.split("_")[-2]
        message_id = info.split("_")[-4]
        wishlist_element_id = info.split("_")[-3]
    wishlist_element: WishlistElement = find_wishlist_element_by_id(wishlist_element_id)
    wishlist: Wishlist = find_wishlist_by_id(wishlist_element.wishlist_id)
    links = wishlist_element.links
    title = f"{wishlist.title.upper()}  –  "
    message = WISHLIST_HEADER % title
    if links:
        message += f"Hai aggiunto  <code>{len(links)}</code>  link per <b>{wishlist_element.description}</b>.\n"
        wishlist_element.links.reverse()
        if len(wishlist_element.links) == 10:
            spaces = "  "
        else:
            spaces = ""
        for index, wishlist_link in enumerate(wishlist_element.links):
            if index == 9:
                spaces = ""
            if len(wishlist_link) > MAX_LINK_LENGTH:
                wishlist_link = '<a href="%s">%s...</a>' % (
                    wishlist_link,
                    wishlist_link[:MAX_LINK_LENGTH],
                )
            if index == 0:
                if len(wishlist_element.links) > 1:
                    message += f"\n{spaces}<b>{index+1}.</b>  {wishlist_link}"
                else:
                    message += f"\n{spaces}<b>{index+1}.</b>  {wishlist_link}"
            elif index == len(wishlist_element.links) - 1:
                message += f"\n\n{spaces}<b>{index+1}.</b>  {wishlist_link}"
            else:
                message += f"\n\n{spaces}<b>{index+1}.</b>  {wishlist_link}"
    else:
        message += (
            f"Qui puoi aggiungere dei link per <b>{wishlist_element.description}</b>."
        )
    if len(links) == MAX_LINKS_NUMBER:
        message += WISHLIST_LINK_LIMIT_REACHED
    keyboard: InlineKeyboardMarkup = view_wishlist_element_links_keyboard(
        wishlist_element_id, page, wishlist_element.links
    )
    context.bot.edit_message_text(
        message_id=message_id,
        chat_id=chat.id,
        text=message,
        reply_markup=keyboard,
        disable_web_page_preview=True,
        parse_mode="HTML",
    )


def ask_for_new_link(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    message_id: int = message.message_id
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    if update.callback_query:
        data = update.callback_query.data
        wishlist_element_id = data.split("_")[-1]
        page = data.split("_")[-2]
        wishlist_element: WishlistElement = find_wishlist_element_by_id(
            wishlist_element_id
        )
        from_wishlist = len(wishlist_element.links) == 0
        info: str = "%s_%s_%s_%s" % (
            message_id,
            wishlist_element_id,
            page,
            from_wishlist,
        )
        redis_helper.save("%s_%s_new_link_message" % (user.id, user.id), str(info))
        redis_helper.save("%s_%s_duplicated_links" % (user.id, user.id), str([]))
        wishlist_id = get_current_wishlist_id(user.id)
        wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
        title = f"{wishlist.title.upper()}  –  "
        if wishlist_element.links:
            append = ADD_NEW_LINK_MESSAGE_NUMBER_OF_NEW_LINK % (
                len(wishlist_element.links),
                MAX_LINKS_NUMBER,
            )
        else:
            append = ""
        wishlist_element.links.reverse()
        for index, wishlist_link in enumerate(wishlist_element.links):
            if len(wishlist_link) > MAX_LINK_LENGTH:
                wishlist_link = '<a href="%s">%s...</a>' % (
                    wishlist_link,
                    wishlist_link[:MAX_LINK_LENGTH],
                )
            if index == 0:
                if len(wishlist_element.links) > 1:
                    append += f"  ├─  {wishlist_link}"
                else:
                    append += f"  └─  {wishlist_link}"
            elif index == len(wishlist_element.links) - 1:
                append += f"\n  └─  {wishlist_link}"
            else:
                append += f"\n  ├─  {wishlist_link}"
        if wishlist_element.links:
            append += "\n\n"
        message = ADD_NEW_LINK_MESSAGE % (title, append, wishlist_element.description)
        context.bot.edit_message_text(
            message_id=message_id,
            chat_id=chat.id,
            text=message,
            reply_markup=build_new_link_keyboard(page, wishlist_element_id),
            disable_web_page_preview=True,
            parse_mode="HTML",
        )
        return APPEND_LINK


def append_link(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    message_id: int = message.message_id
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    wishlist_link: str = message.text
    context.bot.delete_message(message_id=message_id, chat_id=chat.id)
    info = redis_helper.retrieve("%s_%s_new_link_message" % (user.id, user.id)).decode()
    duplicated_links = eval(
        redis_helper.retrieve("%s_%s_duplicated_links" % (user.id, user.id)).decode()
    )
    # number of links
    wishlist_element_id = info.split("_")[-3]
    message_id = info.split("_")[-4]
    page = info.split("_")[-2]
    wishlist_element: WishlistElement = find_wishlist_element_by_id(wishlist_element_id)
    is_present = False
    for link in wishlist_element.links:
        if not is_present:
            is_present = SequenceMatcher(None, wishlist_link, link).ratio() > 0.9
    if is_present:
        if len(wishlist_link) > MAX_LINK_LENGTH:
            wishlist_link = '<a href="%s">%s...</a>' % (
                wishlist_link,
                wishlist_link[:MAX_LINK_LENGTH],
            )
        duplicated_link = "<s>%s</s>     🚫 <b>DUPLICATO</b>" % wishlist_link
        duplicated_links.insert(0, duplicated_link)
        redis_helper.save(
            "%s_%s_duplicated_links" % (user.id, user.id), str(duplicated_links)
        )
    else:
        duplicated_link = None
        wishlist_element.links.append(wishlist_link)
        wishlist_element.save()
        if len(wishlist_element.links) == MAX_LINKS_NUMBER:
            return complete_operation(update, context)
    wishlist_id = get_current_wishlist_id(user.id)
    wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
    title = f"{wishlist.title.upper()}  –  "
    if wishlist_element.links:
        append = ADD_NEW_LINK_MESSAGE_NUMBER_OF_NEW_LINK % (
            len(wishlist_element.links),
            MAX_LINKS_NUMBER,
        )
    else:
        append = ""
    wishlist_element.links.reverse()
    links = wishlist_element.links
    for index, duplicated_link in enumerate(duplicated_links):
        links.insert(index, duplicated_link)
    for index, wishlist_link in enumerate(links):
        if len(wishlist_link) > MAX_LINK_LENGTH:
            if not "DUPLICATO" in wishlist_link:
                wishlist_link = '<a href="%s">%s...</a>' % (
                    wishlist_link,
                    wishlist_link[:MAX_LINK_LENGTH],
                )
        if index == 0:
            if len(wishlist_element.links) > 1:
                append += f"  ├─  {wishlist_link}"
            else:
                append += f"  └─  {wishlist_link}"
        elif index == len(wishlist_element.links) - 1:
            append += f"\n  └─  {wishlist_link}"
        else:
            append += f"\n  ├─  {wishlist_link}"
    if wishlist_element.links:
        append += "\n\n"
    message = ADD_NEW_LINK_MESSAGE % (title, append, wishlist_element.description)
    keyboard = build_new_link_keyboard_added(page, wishlist_element_id)
    try:
        context.bot.edit_message_text(
            message_id=message_id,
            chat_id=chat.id,
            text=message,
            reply_markup=keyboard,
            disable_web_page_preview=True,
            parse_mode="HTML",
        )
    except BadRequest:
        return APPEND_LINK
    return APPEND_LINK


def complete_operation(update: Update, context: CallbackContext):
    view_wishlist_element_links(update, context)
    return ConversationHandler.END


def show_step_two_toast(update: Update, context: CallbackContext):
    context.bot.answer_callback_query(
        update.callback_query.id, text=SUPPORTED_LINKS_MESSAGE, show_alert=True
    )
    return APPEND_LINK


def cancel_link_append(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    message_id: int = message.message_id
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    info = redis_helper.retrieve("%s_%s_new_link_message" % (user.id, user.id)).decode()
    page = info.split("_")[-2]
    from_wishlist = eval(info.split("_")[-1])
    wishlist_element_id = info.split("_")[-3]
    # if from_wishlist:
    #    update.callback_query.data += "_%s" % page
    #    view_wishlist(update, context)
    # else:
    logger.info("THIS IS THE CALL [%s]" % update.callback_query.data)
    view_wishlist_element_links(update, context)
    logger.info("CLOSING...")
    return ConversationHandler.END


ADD_NEW_LINK_TO_ELEMENT_CONVERSATION = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            callback=ask_for_new_link, pattern="ask_for_wishlist_element_link"
        ),
        CallbackQueryHandler(callback=ask_for_new_link, pattern="afwel_link"),
    ],
    states={
        APPEND_LINK: [
            MessageHandler(Filters.entity("url"), append_link),
            CallbackQueryHandler(
                callback=show_step_two_toast, pattern="show_step_2_advance"
            ),
            CallbackQueryHandler(
                callback=complete_operation, pattern="finish_new_link_insert"
            ),
        ]
    },
    fallbacks=[
        CallbackQueryHandler(
            callback=cancel_link_append, pattern="cancel_new_wishlist_element_link"
        ),
    ],
)
