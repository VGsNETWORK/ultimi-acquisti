#!/usr/bin/env python3
# region
import operator
import re
from root.helper.user_helper import get_current_wishlist_id
from typing import List
from telegram.files.inputmedia import InputMediaPhoto

from telegram_utils.utils.tutils import delete_if_private
from root.contants.messages import (
    WISHLIST_HEADER,
)
from root.helper import wishlist
from root.helper.wishlist_element import (
    find_wishlist_element_for_user,
)
from root.model.wishlist_element import WishlistElement

from root.helper.wishlist import (
    count_all_wishlists_for_user,
    create_wishlist,
    find_default_wishlist,
    find_wishlist_by_id,
    find_wishlist_for_user,
    get_total_wishlist_pages_for_user,
)
from root.model.wishlist import Wishlist
from root.contants.keyboard import (
    add_new_wishlist_keyboard,
    create_other_wishlist_keyboard,
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
from root.handlers.handlers import extractor

# endregion

INSERT_TITLE = range(1)


def view_other_wishlists(
    update: Update,
    context: CallbackContext,
    append: str = None,
    page: int = None,
    edit=False,
):
    message: Message = update.effective_message
    message_id = message.message_id
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    current_wishlist = get_current_wishlist_id(user.id)
    if update.callback_query:
        context.bot.answer_callback_query(update.callback_query.id)
        data = update.callback_query.data
        if "convert" in data:
            messages = redis_helper.retrieve("%s_photos_message" % user.id).decode()
            if messages:
                messages = eval(messages)
            else:
                messages = []
            for m_id in messages:
                try:
                    context.bot.delete_message(chat_id=chat.id, message_id=m_id)
                except BadRequest:
                    pass
    if not page:
        if update.callback_query:
            logger.info(update.callback_query)
            page = int(update.callback_query.data.split("_")[-1])
        else:
            page = 0
    else:
        page = int(page)
        message_id = redis_helper.retrieve(user.id).decode()
    total_pages = get_total_wishlist_pages_for_user(user.id)
    wishlist_element: Wishlist = find_default_wishlist(user.id)
    wishlist_elements: List[Wishlist] = find_wishlist_for_user(user.id, page)
    wishlist_ids = [str(wish.id) for wish in wishlist_elements]
    while current_wishlist in wishlist_ids:
        page += 1
        wishlist_elements: List[Wishlist] = find_wishlist_for_user(user.id, page)
        wishlist_ids = [str(wish.id) for wish in wishlist_elements]
    if page == 0:
        wishlist_elements = list(wishlist_elements)
        wishlist_elements.insert(0, wishlist_element)

    chat: Chat = update.effective_chat
    if chat.type != "private":
        # ignore all requests coming outside a private chat
        return
    logger.info(wishlist_elements)
    if wishlist_elements:
        message = ""
        if append:
            wishlist_elements = list(wishlist_elements)
            wish: WishlistElement = wishlist_elements[0]
            message += f"{append}"
    wishlist_id = get_current_wishlist_id(user.id)
    wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
    message = "%s%s%s" % (
        WISHLIST_HEADER % "",
        "Seleziona o crea una lista:\n\n\n",
        message,
    )
    first_page = page + 1 == 1
    last_page = page + 1 == total_pages
    total_lists = count_all_wishlists_for_user(user.id)
    logger.info(f"The user has {total_lists}")
    if update.callback_query or edit:
        if edit:
            message_id = redis_helper.retrieve("%s_%s_new_wishlist")
            message_id = message_id.decode()
        context.bot.edit_message_text(
            chat_id=chat.id,
            message_id=message_id,
            text=message,
            reply_markup=create_other_wishlist_keyboard(
                page,
                total_pages,
                wishlist_elements,
                first_page,
                last_page,
                0,
                total_lists,
                current_wishlist,
            ),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
        return
    else:
        context.bot.send_message(
            chat_id=chat.id,
            text=message,
            reply_markup=create_other_wishlist_keyboard(
                page,
                total_pages,
                wishlist_elements,
                first_page,
                last_page,
                0,
                total_lists,
            ),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
        return


def add_wishlist(
    update: Update,
    context: CallbackContext,
    cycle_insert: bool = False,
    toggle_cycle: bool = False,
):
    logger.info("received add to wishlist_element")
    message: Message = update.effective_message
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    message_id = message.message_id
    redis_helper.save("%s_%s_new_wishlist", message_id)
    data = update.callback_query.data
    from_element = "from_element" in data
    try:
        message = "Per piacere inserisci il nome della tua wishlist."
        context.bot.edit_message_text(
            message_id=message_id,
            chat_id=chat.id,
            text=message,
            reply_markup=add_new_wishlist_keyboard(from_element),
            disable_web_page_preview=True,
            parse_mode="HTML",
        )
    except BadRequest:
        pass
    return INSERT_TITLE


def handle_add_confirm(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    message_id: int = message.message_id
    user: User = update.effective_user
    cdopohat: Chat = update.effective_chat
    delete_if_private(message)
    message = message.text
    message: str = message.split("\n")[0]
    message: str = re.sub(r"\s{2,}", " ", message)
    if len(message) > 17:
        # THE FUCK YOU'RE DOING
        overload = True
        message = "Hai superato il limite massimo di caratteri..."
    else:
        create_wishlist("", message, user.id)
        overload = False
        view_other_wishlists(update, context, "✅  <i>Lista creata!</i>", "0", True)
    return INSERT_TITLE if overload else ConversationHandler.END


def cancel_add_wishlist(update: Update, context: CallbackContext):
    data = update.callback_query.data
    if not "NO_DELETE" in data:
        user: User = update.effective_user
    update.callback_query.data += "_0"
    view_other_wishlists(update, context)
    return ConversationHandler.END


ADD_NEW_WISHLIST = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(add_wishlist, pattern="add_new_wishlist"),
    ],
    states={
        INSERT_TITLE: [
            MessageHandler(Filters.text, handle_add_confirm),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(cancel_add_wishlist, pattern="cancel_add_to_wishlist"),
    ],
)