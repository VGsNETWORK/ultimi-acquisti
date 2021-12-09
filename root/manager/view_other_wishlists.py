#!/usr/bin/env python3
# region
import operator
import re

from bot_util.decorator.telegram import update_user_information
from root.helper.notification import create_notification

from bs4 import element
from root.helper.redis_message import is_develop
from root.manager import change_element_wishlist
from root.contants.constant import MAX_WISHLIST_NAME_LENGTH
from root.util.util import max_length_error_format
from root.helper.user_helper import get_current_wishlist_id
from typing import List
from telegram.files.inputmedia import InputMediaPhoto
from random import randint

from telegram_utils.utils.tutils import delete_if_private, log
from root.contants.messages import (
    ADD_WISHLIST_TITLE_PROMPT,
    NOTIFICATION_NEW_WISHLIST,
    NOTIFICATION_REORDER_WISHLIST_DOWN,
    NOTIFICATION_REORDER_WISHLIST_UP,
    WISHLIST_DESCRIPTION_TOO_LONG,
    WISHLIST_HEADER,
    WISHLIST_LIST_LEGEND_HAS_ELEMENTS,
    WISHLIST_LIST_LEGEND_HAS_PHOTOS,
    WISHLIST_LIST_LEGEND_REMOVE_ALL,
    WISHLIST_LIST_LEGEND_REMOVE_ONLY_ITEMS,
    WISHLIST_LIST_LEGEND_REORDER_DOWN,
    WISHLIST_LIST_LEGEND_REORDER_UP,
    WISHLIST_LIST_MESSAGE,
    WISHLIST_TITLE_TOO_LONG,
)
from root.helper import wishlist
from root.helper.wishlist_element import (
    count_all_wishlist_elements_for_wishlist_id,
    count_all_wishlist_elements_photos,
    find_wishlist_element_for_user,
)
from root.model.wishlist_element import WishlistElement

from root.helper.wishlist import (
    count_all_wishlists_for_user,
    create_wishlist,
    find_default_wishlist,
    find_wishlist_by_for_index,
    find_wishlist_by_id,
    find_wishlist_for_user,
    get_total_wishlist_pages_for_user,
)
from root.model.wishlist import Wishlist
from root.contants.keyboard import (
    add_new_wishlist_keyboard,
    add_new_wishlist_too_long_keyboard,
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


def reorder_wishlist(update: Update, context: CallbackContext):
    context.bot.answer_callback_query(update.callback_query.id)
    message: Message = update.effective_message
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    user_id: int = user.id
    chat_id: int = chat.id
    message_id: message.message_id
    data = update.callback_query.data
    wishlist_id: str = data.split("_")[-1]
    wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
    if wishlist:
        if "down" in data:
            if wishlist.index < 9:
                logger.info("SEARCHING WISHLIST WITH INDEX %s" % (wishlist.index - 1))
                other_wishlist: Wishlist = find_wishlist_by_for_index(
                    wishlist.index - 1, user_id
                )
                if other_wishlist:
                    wishlist.index, other_wishlist.index = (
                        other_wishlist.index,
                        wishlist.index,
                    )
                    other_wishlist.save()
                    wishlist.save()
                    wishlists = find_wishlist_for_user(user_id)
                    wishlists = list(wishlists)
                    wishlists.sort(key=lambda x: x.index, reverse=True)
                    message = "\n".join(
                        [
                            f"    <b>{wishlist.index}.</b>  <i>{wishlist.title}</i>"
                            for wishlist in wishlists
                        ]
                    )
                    notification_message = NOTIFICATION_REORDER_WISHLIST_DOWN % (
                        wishlist.title,
                        other_wishlist.title,
                        message,
                    )
                    create_notification(update.effective_user.id, notification_message)
        elif "up" in data:
            if wishlist.index > 0:
                logger.info("SEARCHING WISHLIST WITH INDEX %s" % (wishlist.index + 1))
                other_wishlist: Wishlist = find_wishlist_by_for_index(
                    wishlist.index + 1, user_id
                )
                if other_wishlist:
                    wishlist.index, other_wishlist.index = (
                        other_wishlist.index,
                        wishlist.index,
                    )
                    other_wishlist.save()
                    wishlist.save()
                    wishlists = find_wishlist_for_user(user_id)
                    wishlists = list(wishlists)
                    wishlists.sort(key=lambda x: x.index, reverse=True)
                    message = "\n".join(
                        [
                            f"    <b>{wishlist.index}.</b>  <i>{wishlist.title}</i>"
                            for wishlist in wishlists
                        ]
                    )
                    notification_message = NOTIFICATION_REORDER_WISHLIST_UP % (
                        wishlist.title,
                        other_wishlist.title,
                        message,
                    )
                    create_notification(update.effective_user.id, notification_message)
        if is_develop():
            wishlists = list(find_wishlist_for_user(user_id))
            wishlists.sort(key=lambda x: x.index, reverse=True)
            message = (
                "Nuovo ordine delle liste dei desideri"
                f' per <a href="tg://user?id={user_id}">{user_id}</a>:\n'
            )
            message += "\n".join(
                [
                    f"    <b>{wishlist.index}.</b>  <i>{wishlist.title}</i>"
                    for wishlist in wishlists
                ]
            )
            log(0, message, disable_notification=True)
    try:
        update.callback_query.data += "_0"
        view_other_wishlists(update, context)
    except BadRequest as e:
        logger.error(e)


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
            append = f"\n\n\n{append}"
        else:
            append = f""
    wishlist_id = get_current_wishlist_id(user.id)
    wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
    has_elements = False
    has_photo = False
    for wishlist_element in wishlist_elements:
        if (
            count_all_wishlist_elements_for_wishlist_id(
                str(wishlist_element.id), user.id
            )
            > 0
        ):
            has_elements = True
        if (count_all_wishlist_elements_photos(user.id, str(wishlist_element.id))) > 0:
            has_photo = True
    before_pencil = ""
    empty_list_legend = ""
    other_list_legend = ""
    if len(wishlist_elements) > 2:
        before_pencil += WISHLIST_LIST_LEGEND_REORDER_UP
        before_pencil += WISHLIST_LIST_LEGEND_REORDER_DOWN
    if has_elements:
        empty_list_legend += WISHLIST_LIST_LEGEND_REMOVE_ONLY_ITEMS
        other_list_legend += WISHLIST_LIST_LEGEND_HAS_ELEMENTS
    if has_photo:
        other_list_legend += WISHLIST_LIST_LEGEND_HAS_PHOTOS
    if len(wishlist_elements) > 1:
        empty_list_legend += WISHLIST_LIST_LEGEND_REMOVE_ALL
    message = "%s%s" % (
        WISHLIST_HEADER % "",
        f"{WISHLIST_LIST_MESSAGE % (before_pencil, empty_list_legend, other_list_legend)}{append}",
    )
    first_page = page + 1 == 1
    last_page = page + 1 == total_pages
    total_lists = count_all_wishlists_for_user(user.id)
    logger.info(f"The user has {total_lists}")
    if update.callback_query or edit:
        if edit:
            if not update.callback_query:
                message_id = redis_helper.retrieve(
                    "%s_%s_new_wishlist" % (user.id, user.id)
                )
                message_id = message_id.decode()
            else:
                message_id = update.effective_message.message_id
        previous = redis_helper.retrieve("%s_%s_previous_value" % (user.id, user.id))
        if previous:
            previous = previous.decode()
            previous = int(previous)
        else:
            previous = 0
        n = randint(1, 10)
        while n == previous:
            n = randint(1, 10)
        redis_helper.save("%s_%s_previous_value" % (user.id, user.id), str(n))
        message += "&#8203;" * n
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
                user.id,
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
                user.id,
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
    redis_helper.save("%s_%s_new_wishlist" % (user.id, user.id), message_id)
    data = update.callback_query.data
    from_element = "from_element" in data
    from_move = "from_move" in data
    redis_helper.save("%s_%s_from_move" % (user.id, user.id), str(from_move))
    wish_id = data.split("_")[-1]
    index = data.split("_")[-2]
    redis_helper.save(
        "%s_%s_from_move_info" % (user.id, user.id), "%s_%s" % (index, wish_id)
    )
    logger.info("FROM MOVE %s" % from_move)
    try:
        message = f"{WISHLIST_HEADER % ''}{ADD_WISHLIST_TITLE_PROMPT % MAX_WISHLIST_NAME_LENGTH}"
        context.bot.edit_message_text(
            message_id=message_id,
            chat_id=chat.id,
            text=message,
            reply_markup=add_new_wishlist_keyboard(
                from_element, from_move, index, wish_id
            ),
            disable_web_page_preview=True,
            parse_mode="HTML",
        )
    except BadRequest:
        pass
    return INSERT_TITLE


def handle_add_confirm(update: Update, context: CallbackContext, edit: bool = False):
    message: Message = update.effective_message
    message_id: int = message.message_id
    logger.info("REAL_MESSAGE_ID: %s" % message_id)
    chat_id: int = update.effective_chat.id
    user: User = update.effective_user
    cdopohat: Chat = update.effective_chat
    delete_if_private(message)
    message = message.text
    message: str = message.split("\n")[0]
    message: str = re.sub(r"\s{2,}", " ", message)
    if len(message) > MAX_WISHLIST_NAME_LENGTH:
        logger.info("TOO LONG")
        redis_helper.save(
            "%s_stored_wishlist" % user.id,
            update.effective_message.text[:MAX_WISHLIST_NAME_LENGTH],
        )
        user_text = max_length_error_format(
            update.effective_message.text, MAX_WISHLIST_NAME_LENGTH, 100
        )
        message = f"{WISHLIST_HEADER % ''}{user_text}\n{WISHLIST_TITLE_TOO_LONG % MAX_WISHLIST_NAME_LENGTH}{ADD_WISHLIST_TITLE_PROMPT % MAX_WISHLIST_NAME_LENGTH}"
        overload = True
        message_id = redis_helper.retrieve(
            "%s_%s_new_wishlist" % (user.id, user.id)
        ).decode()
        data = redis_helper.retrieve(
            "%s_%s_from_move_info" % (user.id, user.id)
        ).decode()
        index = data.split("_")[-2]
        wish_id = data.split("_")[-1]
        from_move = redis_helper.retrieve(
            "%s_%s_from_move" % (user.id, user.id)
        ).decode()
        logger.info("TOO LONG FROM MOVE %s" % from_move)
        from_move = eval(from_move)
        context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=message,
            # TODO: fix
            reply_markup=add_new_wishlist_too_long_keyboard(
                False, from_move, index, wish_id
            ),
            parse_mode="HTML",
            disable_web_page_preview=False,
        )
    else:
        create_wishlist("", message, user.id)
        logger.info("THE FUXK")
        overload = False
        from_move = redis_helper.retrieve(
            "%s_%s_from_move" % (user.id, user.id)
        ).decode()
        logger.info("FROM MOVE %s" % from_move)
        from_move = eval(from_move)
        if from_move:
            message_id = redis_helper.retrieve(
                "%s_%s_new_wishlist" % (user.id, user.id)
            ).decode()
            data = redis_helper.retrieve(
                "%s_%s_from_move_info" % (user.id, user.id)
            ).decode()
            index = data.split("_")[-2]
            wish_id = data.split("_")[-1]
            change_element_wishlist.ask_wishlist_change(
                update, context, index, wish_id, message_id
            )
        else:
            logger.info("AGGIUNTA")
            view_other_wishlists(
                update,
                context,
                f"✅  <i>Lista <b>{message}</b> creata!</i>",
                "0",
                True,
            )
    if not overload:
        count = count_all_wishlists_for_user(user_id=update.effective_user.id)
        notification_message = NOTIFICATION_NEW_WISHLIST % (message, count)
        create_notification(update.effective_user.id, notification_message)
        if is_develop():
            message = f"USER_ID: {user.id}\n"
            wishlists = find_wishlist_for_user(user.id)
            wishlists = list(wishlists)
            wishlists.sort(key=lambda x: x.index, reverse=True)
            if is_develop():
                user_id = update.effective_user.id
                wishlists = list(find_wishlist_for_user(user_id))
                wishlists.sort(key=lambda x: x.index, reverse=True)
                message = (
                    "Nuovo ordine delle liste dei desideri"
                    f' per <a href="tg://user?id={user_id}">{user_id}</a>:\n'
                )
                message += "\n".join(
                    [
                        f"    <b>{wishlist.index}.</b>  <i>{wishlist.title}</i>"
                        for wishlist in wishlists
                    ]
                )
                log(0, message, disable_notification=True)
        pass
    return INSERT_TITLE if overload else ConversationHandler.END


def cancel_add_wishlist(update: Update, context: CallbackContext):
    logger.info("CANCEL")
    data = update.callback_query.data
    if not "NO_DELETE" in data:
        user: User = update.effective_user
    if not "from_move" in update.callback_query.data:
        update.callback_query.data += "_0"
        view_other_wishlists(update, context)
    else:
        change_element_wishlist.ask_wishlist_change(update, context)
    return ConversationHandler.END


def handle_keep_confirm(update: Update, context: CallbackContext):
    user: User = update.effective_user
    message = redis_helper.retrieve("%s_stored_wishlist" % user.id).decode()
    create_wishlist("", message, user.id)
    logger.info(update.callback_query.data)
    if not "from_move" in update.callback_query.data:
        view_other_wishlists(
            update,
            context,
            f"✅  <i>Lista <b>{message}</b> creata!</i>",
            "0",
            True,
        )
    else:
        change_element_wishlist.ask_wishlist_change(update, context)
    if is_develop():
        message = f"USER_ID: {user.id}\n"
        wishlists = find_wishlist_for_user(user.id)
        wishlists = list(wishlists)
        wishlists.sort(key=lambda x: x.index, reverse=True)
        message += "\n".join(
            [
                f"    —  <b>{wishlist.title}</b>: <i>{wishlist.index}</i>"
                for wishlist in wishlists
            ]
        )
        log(0, message, disable_notification=True)
    return ConversationHandler.END


ADD_NEW_WISHLIST = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(add_wishlist, pattern="add_new_wishlist"),
    ],
    states={
        INSERT_TITLE: [
            MessageHandler(Filters.text, handle_add_confirm),
            CallbackQueryHandler(handle_keep_confirm, pattern="keep_the_current"),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(cancel_add_wishlist, pattern="cancel_add_to_wishlist"),
    ],
)