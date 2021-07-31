#!/usr/bin/env python3


from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
import telegram_utils.utils.logger as logger
from root.model.wishlist import Wishlist
from root.contants.keyboard import view_wishlist_element_links_keyboard
from root.contants.messages import WISHLIST_HEADER
from root.helper.wishlist_element import find_wishlist_element_by_id
from root.helper.wishlist import find_wishlist_by_id
from root.model.wishlist_element import WishlistElement
from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update
from root.model.user import User
from telegram.chat import Chat
from telegram.message import Message


def view_wishlist_element_links(
    update: Update,
    context: CallbackContext,
    append: str = None,
):
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
        wishlist: Wishlist = find_wishlist_by_id(wishlist_element.wishlist_id)
        links = wishlist_element.links
        title = f"{wishlist.title.upper()}  –  "
        message = WISHLIST_HEADER % title
        message += f"<b>{wishlist_element.description}</b>"
        for index, link in enumerate(links):
            index += 1
            if len(link) > 40:
                message += f'\n{index}.  <a href="{link}">{link[:40]}</a>'
            else:
                message += f"\n{index}.  {link}"
        keyboard: InlineKeyboardMarkup = view_wishlist_element_links_keyboard(
            wishlist_element_id, page, links
        )
        context.bot.edit_message_text(
            message_id=message_id,
            chat_id=chat.id,
            text=message,
            reply_markup=keyboard,
            disable_web_page_preview=True,
            parse_mode="HTML",
        )