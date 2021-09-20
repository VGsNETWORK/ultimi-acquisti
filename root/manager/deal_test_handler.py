#!/usr/bin/env python3


from root.helper.notification import create_notification
from root.util.util import format_error, format_price
from telegram.chat import Chat
from telegram.error import BadRequest
from root.model.wishlist_element import WishlistElement
from root.helper.wishlist_element import find_containing_link
from typing import List
from root.helper.tracked_link_helper import get_paged_link_for_user
from root.model.tracked_link import TrackedLink
from telegram.user import User
from telegram.update import Update
from telegram.message import Message
from root.contants.messages import DEAL_MESSAGE_FORMAT, DEAL_MESSAGE_FORMAT_APPEND
from telegram.ext.callbackcontext import CallbackContext
from telegram_utils.utils.tutils import delete_if_private
import telegram_utils.utils.logger as logger
import math


def command_send_deal(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    delete_if_private(message)
    if message.chat.type != "private":
        return
    tracked_link: List[TrackedLink] = get_paged_link_for_user(
        user.id, page=0, page_size=1
    )
    if tracked_link:
        tracked_link: TrackedLink = tracked_link[0]
        element: WishlistElement = find_containing_link(user.id, tracked_link.link)
        price: float = tracked_link.price + 20.00
        perc = math.ceil((price - tracked_link.price) * price / 100)
        text = DEAL_MESSAGE_FORMAT % (
            tracked_link.link,
            element.description,
            perc,
            format_price(price - tracked_link.price),
            format_price(tracked_link.price),
            DEAL_MESSAGE_FORMAT_APPEND if perc > 30 else "",
        )
        logger.info(text)
        try:
            context.bot.send_message(
                chat_id=chat.id,
                text=text,
                disable_web_page_preview=True,
                parse_mode="HTML",
            )
            create_notification(user.id, text)
        except BadRequest as br:
            logger.error(format_error(br))
