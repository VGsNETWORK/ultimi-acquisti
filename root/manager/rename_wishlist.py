#!/usr/bin/env python3
# region
import operator
import re
from root.helper.notification import create_notification
from root.contants.constant import MAX_WISHLIST_NAME_LENGTH
from root.util.util import max_length_error_format
from root.helper.user_helper import get_current_wishlist_id
from typing import List
from telegram.files.inputmedia import InputMediaPhoto
from telegram_utils.utils.tutils import delete_if_private
from root.manager.view_other_wishlists import view_other_wishlists
from root.contants.messages import (
    ADD_WISHLIST_TITLE_PROMPT,
    EDIT_WISHLIST_PROMPT,
    EDIT_WISHLIST_TITLE_PROMPT,
    NOTIFICATION_WISHLIST_NAME_CHANGED,
    WISHLIST_DESCRIPTION_TOO_LONG,
    WISHLIST_HEADER,
    WISHLIST_TITLE_TOO_LONG,
)
from root.helper import wishlist
from root.helper.wishlist_element import (
    find_wishlist_element_for_user,
)
from root.model.wishlist_element import WishlistElement

from root.helper.wishlist import (
    change_wishlist_title,
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
    edit_wishlist_name_keyboard,
    create_other_wishlist_keyboard,
    edit_wishlist_name_too_long_keyboard,
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
from bot_util.decorator.maintenance import check_maintenance

# endregion

EDIT_TITLE = range(1)


@check_maintenance
def edit_wishlist(
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
    redis_helper.save("%s_%s_new_wishlist" % (user.id, user.id), message_id)
    data = update.callback_query.data
    wishlist_id = data.split("_")[-1]
    redis_helper.save("%s_%s_edit_wishlist_id" % (user.id, user.id), wishlist_id)
    wishlist = find_wishlist_by_id(wishlist_id)
    try:
        message = (
            f"{WISHLIST_HEADER % ''}{EDIT_WISHLIST_TITLE_PROMPT % (wishlist.title, 15)}"
        )
        context.bot.edit_message_text(
            message_id=message_id,
            chat_id=chat.id,
            text=message,
            reply_markup=edit_wishlist_name_keyboard(False),
            disable_web_page_preview=True,
            parse_mode="HTML",
        )
    except BadRequest:
        pass
    return EDIT_TITLE


@check_maintenance
def handle_add_confirm(update: Update, context: CallbackContext, edit: bool = False):
    message: Message = update.effective_message
    message_id: int = message.message_id
    chat_id: int = update.effective_chat.id
    user: User = update.effective_user
    delete_if_private(message)
    message = message.text
    message: str = re.sub(r"\n{1,}", "\n", message)
    message: str = re.sub(r"\s{2,}", " ", message)
    if len(message) > MAX_WISHLIST_NAME_LENGTH:
        wishlist_id = redis_helper.retrieve(
            "%s_%s_edit_wishlist_id" % (user.id, user.id)
        ).decode()
        wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
        logger.info("TOO LONG")
        redis_helper.save(
            "%s_stored_wishlist" % user.id, message[:MAX_WISHLIST_NAME_LENGTH]
        )
        user_text = max_length_error_format(message, MAX_WISHLIST_NAME_LENGTH, 100)
        message = f"{WISHLIST_HEADER % ''}\"{user_text}\"\n{WISHLIST_TITLE_TOO_LONG % MAX_WISHLIST_NAME_LENGTH}{EDIT_WISHLIST_TITLE_PROMPT % (wishlist.title, MAX_WISHLIST_NAME_LENGTH)}"
        overload = True
        message_id = redis_helper.retrieve(
            "%s_%s_new_wishlist" % (user.id, user.id)
        ).decode()
        context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=message,
            reply_markup=edit_wishlist_name_too_long_keyboard(False),
            parse_mode="HTML",
            disable_web_page_preview=False,
        )
    else:
        wishlist_id: str = redis_helper.retrieve(
            "%s_%s_edit_wishlist_id" % (user.id, user.id)
        ).decode()
        wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
        old_name = wishlist.title
        change_wishlist_title(wishlist_id, message)
        overload = False
        notification_message = NOTIFICATION_WISHLIST_NAME_CHANGED % (old_name, message)
        create_notification(update.effective_user.id, notification_message)
        view_other_wishlists(
            update,
            context,
            f"✅  <i>Lista {old_name} rinominata in <b>{message}</b>!</i>",
            "0",
            True,
        )
    return EDIT_TITLE if overload else ConversationHandler.END


@check_maintenance
def cancel_edit_wishlist(update: Update, context: CallbackContext):
    update.callback_query.data += "_0"
    view_other_wishlists(update, context)
    return ConversationHandler.END


@check_maintenance
def handle_keep_confirm(update: Update, context: CallbackContext):
    user: User = update.effective_user
    message = redis_helper.retrieve("%s_stored_wishlist" % user.id).decode()
    wishlist_id: str = redis_helper.retrieve(
        "%s_%s_edit_wishlist_id" % (user.id, user.id)
    ).decode()
    change_wishlist_title(wishlist_id, message)
    view_other_wishlists(
        update,
        context,
        f"✅  <i>Lista <b>{message}</b> rinominata!</i>",
        "0",
        True,
    )
    return ConversationHandler.END


EDIT_WISHLIST_NAME = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(edit_wishlist, pattern="edit_wishlist_name"),
    ],
    states={
        EDIT_TITLE: [
            MessageHandler(Filters.text, handle_add_confirm),
            CallbackQueryHandler(handle_keep_confirm, pattern="confirm_edit"),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(cancel_edit_wishlist, pattern="cancel_edit_wishlist"),
    ],
)
