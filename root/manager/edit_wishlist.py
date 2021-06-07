#!/usr/bin/env python3

from root.manager.whishlist import view_wishlist
from root.util.util import extract_first_link_from_message, max_length_error_format
from root.model.user import User
import telegram_utils.helper.redis as redis_helper
from telegram.chat import Chat
from telegram.message import Message
from root.contants.keyboard import (
    build_edit_wishlist_desc_keyboard,
    build_edit_wishlist_link_keyboard,
)
from root.contants.messages import (
    ADD_LINK_TO_WISHLIST_ITEM_MESSAGE,
    EDIT_LINK_TO_WISHLIST_ITEM_MESSAGE,
    EDIT_WISHLIST_PROMPT,
    WISHLIST_DESCRIPTION_TOO_LONG,
    WISHLIST_STEP_ONE,
    WISHLIST_STEP_TWO,
)
from root.helper.wishlist import find_wishlist_by_id
from root.model.wishlist import Wishlist
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.ext.conversationhandler import ConversationHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
import telegram_utils.utils.logger as logger

EDIT_WISHLIST_TEXT, EDIT_ZELDA = range(2)


def edit_wishlist_item(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    message_id = message.message_id
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    redis_helper.save(user.id, message_id)
    _id = update.callback_query.data.split("_")[-1]
    page = int(update.callback_query.data.split("_")[-2])
    wish: Wishlist = find_wishlist_by_id(_id)
    index = update.callback_query.data.split("_")[-3]
    redis_helper.save("%s_%s" % (user.id, user.id), "%s_%s_%s" % (index, page, _id))
    message = f"<b><u>LISTA DEI DESIDERI</u></b>\n\n\n"
    append = "✏️  <i>Stai modificando questo elemento</i>"
    if wish.link:
        message += f'<b>{index}</b>  <b><a href="{wish.link}"><b>{wish.description}</b></a></b>\n{append}\n\n'
    else:
        message += f"<b>{index}</b>  <b>{wish.description}</b>\n{append}\n\n"
    message += "\n%s%s" % (WISHLIST_STEP_ONE, EDIT_WISHLIST_PROMPT)
    keyboard = build_edit_wishlist_desc_keyboard(_id, page, index)
    context.bot.edit_message_text(
        chat_id=chat.id,
        text=message,
        message_id=message_id,
        reply_markup=keyboard,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
    return EDIT_WISHLIST_TEXT


def edit_wishlist_description(update: Update, context: CallbackContext):
    logger.info("EDIT_WISHLIST_DESCRIPTION")
    message: Message = update.effective_message
    message_id: int = message.message_id
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    if update.callback_query:
        _id = update.callback_query.data.split("_")[-1]
        page = int(update.callback_query.data.split("_")[-2])
        index = update.callback_query.data.split("_")[-3]
        text = ""
    else:
        context.bot.delete_message(chat_id=chat.id, message_id=message_id)
        message_id = redis_helper.retrieve(user.id).decode()
        data = redis_helper.retrieve("%s_%s" % (user.id, user.id)).decode()
        _id = data.split("_")[-1]
        page = int(data.split("_")[-2])
        index = data.split("_")[-3]
        text = message.text

    wish: Wishlist = find_wishlist_by_id(_id)
    if update.callback_query:
        if "keep_current_description" in update.callback_query.data:
            text = wish.description
        if "confirm_description_mod" in update.callback_query.data:
            text = redis_helper.retrieve("%s_stored_wishlist" % user.id).decode()
    if len(text) > 128:
        redis_helper.save(
            "%s_stored_wishlist" % user.id, update.effective_message.text[:128]
        )
        user_text = max_length_error_format(
            update.effective_message.text, 128, 200, wish.link
        )
        message = (
            f"<b><u>LISTA DEI DESIDERI</u></b>\n\n\n<b>1.</b>  {user_text}\n"
            f"{WISHLIST_DESCRIPTION_TOO_LONG}"
        )
        message += "\n%s%s" % (WISHLIST_STEP_ONE, EDIT_WISHLIST_PROMPT)
        keyboard = build_edit_wishlist_desc_keyboard(_id, page, index, True)
        redis_helper.save(
            "%s_stored_wishlist" % user.id, update.effective_message.text[:128]
        )
    else:
        ask = "*" if not wish.description == text else ""
        wish.description = text
        redis_helper.save("%s_stored_wishlist" % user.id, text)
        message = f"<b><u>LISTA DEI DESIDERI</u></b>\n\n\n"
        append = "✏️  <i>Stai modificando questo elemento</i>"
        if wish.link:
            message += f'<b>{index}</b>  {ask}<b><a href="{wish.link}">{wish.description}</a></b>\n{append}\n\n'
        else:
            message += f"<b>{index}</b>  {ask}<b>{wish.description}</b>\n{append}\n\n"
        if not wish.link:
            message += "\n%s%s" % (WISHLIST_STEP_TWO, ADD_LINK_TO_WISHLIST_ITEM_MESSAGE)
        else:
            message += "\n%s%s" % (
                WISHLIST_STEP_TWO,
                EDIT_LINK_TO_WISHLIST_ITEM_MESSAGE,
            )
        keyboard = build_edit_wishlist_link_keyboard(_id, page, index, wish.link)
    context.bot.edit_message_text(
        chat_id=chat.id,
        text=message,
        message_id=message_id,
        reply_markup=keyboard,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
    return EDIT_ZELDA if len(text) <= 128 else EDIT_WISHLIST_TEXT


def edit_wishlist_link(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    message_id: int = message.message_id
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    text = redis_helper.retrieve("%s_stored_wishlist" % user.id).decode()
    if update.callback_query:
        _id = update.callback_query.data.split("_")[-1]
    else:
        context.bot.delete_message(chat_id=chat.id, message_id=message_id)
        message_id = redis_helper.retrieve(user.id).decode()
        data = redis_helper.retrieve("%s_%s" % (user.id, user.id)).decode()
        _id = data.split("_")[-1]
        link = message.text if message.text else message.caption
        link = extract_first_link_from_message(update.effective_message)
        logger.info(link)
    wish: Wishlist = find_wishlist_by_id(_id)
    wish.description = text
    if update.callback_query:
        if "remove_link" in update.callback_query.data:
            wish.link = ""
    else:
        wish.link = link
    wish.save()
    cancel_edit_wishlist(update, context)
    return ConversationHandler.END


def cancel_edit_wishlist(update: Update, context: CallbackContext):
    if update.callback_query:
        page = update.callback_query.data.split("_")[-2]
        update.callback_query.data += "_%s" % page
        view_wishlist(update, context)
    else:
        view_wishlist(update, context, None, "0")
    return ConversationHandler.END


EDIT_WISHLIST_CONVERSATION = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            edit_wishlist_item,
            pattern="edit_wishlist_item",
        ),
    ],
    states={
        EDIT_WISHLIST_TEXT: [
            MessageHandler(
                Filters.text,
                edit_wishlist_description,
            ),
            CallbackQueryHandler(
                callback=edit_wishlist_description, pattern="keep_current_description"
            ),
            CallbackQueryHandler(
                callback=edit_wishlist_description, pattern="confirm_description_mod"
            ),
        ],
        EDIT_ZELDA: [
            MessageHandler(Filters.entity("url"), edit_wishlist_link),
            CallbackQueryHandler(
                callback=edit_wishlist_link, pattern="keep_current_link"
            ),
            CallbackQueryHandler(
                callback=edit_wishlist_link,
                pattern="remove_link",
            ),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(
            cancel_edit_wishlist,
            pattern="cancel_edit_wishlist",
        ),
    ],
)