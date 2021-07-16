#!/usr/bin/env python3

from root.contants.messages import CHANGE_ELEMENT_WISHLIST_MESSAGE, WISHLIST_CHANGED
from root.helper import wishlist
from root.model.wishlist_element import WishlistElement
from root.manager.wishlist_element import view_wishlist
from root.contants.keyboard import choose_new_wishlist_keyboard
from root.helper.wishlist import (
    find_wishlist_by_id,
    find_wishlist_not_id,
)
from typing import List
from root.model.wishlist import Wishlist
from root.helper.wishlist_element import (
    count_all_wishlist_elements_for_wishlist_id,
    find_wishlist_element_by_id,
)
from telegram.ext import ConversationHandler
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.update import Update
import telegram_utils.utils.logger as logger
from time import sleep

CHANGE_ELEMENT_WISHLIST = range(1)


def ask_wishlist_change(update: Update, context: CallbackContext):
    message_id: int = update.effective_message.message_id
    chat_id: int = update.effective_chat.id
    user_id = update.effective_user.id
    data: str = update.callback_query.data
    wishlist_element_id: str = data.split("_")[-1]
    index: str = data.split("_")[-2]
    wishlist_element: WishlistElement = find_wishlist_element_by_id(wishlist_element_id)
    wishlist_id: str = wishlist_element.wishlist_id
    wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
    wishlists: List[Wishlist] = find_wishlist_not_id(wishlist_id, user_id)
    keyboard = choose_new_wishlist_keyboard(wishlists, wishlist_element_id)
    title = f"{wishlist.title.upper()}  –  "
    message = CHANGE_ELEMENT_WISHLIST_MESSAGE % (
        title,
        index,
        wishlist_element.description,
    )
    context.bot.edit_message_text(
        message_id=message_id,
        chat_id=chat_id,
        text=message,
        reply_markup=keyboard,
        disable_web_page_preview=True,
        parse_mode="HTML",
    )
    return CHANGE_ELEMENT_WISHLIST


def change_wishlist(update: Update, context: CallbackContext):
    user: User = update.effective_user
    data: str = update.callback_query.data
    wishlist_element_id: str = data.split("_")[-1]
    wishlist_id: str = data.split("_")[-2]
    wishlist_element: WishlistElement = find_wishlist_element_by_id(wishlist_element_id)
    wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
    logger.info(f"THIS IS THE TITLE: {wishlist.title}")
    old_wishlist: str = wishlist_element.wishlist_id
    wishlist_element.wishlist_id = str(wishlist.id)
    wishlist_element.save()
    update.callback_query.data += "_0"
    append = WISHLIST_CHANGED % (wishlist_element.description, wishlist.title)
    view_wishlist(update, context, append=append, under_first=False)
    return ConversationHandler.END


def cancel_wishlist_change(update: Update, context: CallbackContext):
    update.callback_query.data += "_0"
    view_wishlist(update, context)
    return ConversationHandler.END


CHANGE_WISHLIST_ELEMENT_LIST = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            ask_wishlist_change,
            pattern="ask_element_wishlist_change",
        )
    ],
    states={
        CHANGE_ELEMENT_WISHLIST: [CallbackQueryHandler(change_wishlist, pattern="cwel")]
    },
    fallbacks=[
        CallbackQueryHandler(
            cancel_wishlist_change,
            pattern="cancel_wishlist_change",
        )
    ],
)
