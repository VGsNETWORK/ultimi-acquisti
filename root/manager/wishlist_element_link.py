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


def delete_wishlist_element_link(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    message_id: int = message.message_id
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    if update.callback_query:
        data = update.callback_query.data
        wishlist_element_id = data.split("_")[-1]
        page = data.split("_")[-2]
        index = int(data.split("_")[-3])
        wishlist_element: WishlistElement = find_wishlist_element_by_id(
            wishlist_element_id
        )
        links = wishlist_element.links
        links.pop(index)
        wishlist_element.links = links
        wishlist_element.save()
        view_wishlist_element_links(update, context)
    return


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
        if links:
            message += f"Hai aggiunto  <code>{len(links)}</code>  link per <b>{wishlist_element.description}</b>.\n"
            for index, wishlist_link in enumerate(links):
                if len(wishlist_link) > 27:
                    wishlist_link = '<a href="%s">%s...</a>' % (
                        wishlist_link,
                        wishlist_link[:27],
                    )
                if index == 0:
                    if len(wishlist_element.links) > 1:
                        message += f"  │\n  ├─    <b>{index+1}.</b>  {wishlist_link}"
                    else:
                        message += f"  │\n  └─    <b>{index+1}.</b>  {wishlist_link}"
                elif index == len(wishlist_element.links) - 1:
                    message += f"\n  │\n  └─    <b>{index+1}.</b>  {wishlist_link}"
                else:
                    message += f"\n  │\n  ├─    <b>{index+1}.</b>  {wishlist_link}"
        else:
            message += f"Qui puoi aggiungere delle foto per <b>{wishlist_element.description}</b>."
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