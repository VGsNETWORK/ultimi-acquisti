#!/usr/bin/env python3
# region
from datetime import datetime
import enum
import operator
import re
from difflib import SequenceMatcher
from root.model import notification
from typing import List

import emoji
import telegram_utils.helper.redis as redis_helper
import telegram_utils.utils.logger as logger
from root.contants.constant import CATEGORIES
from root.contants.keyboard import (
    ADD_LINK_TO_WISHLIST_ITEM,
    ADD_LINK_TO_WISHLIST_ITEM_NO_LINK,
    ADD_TO_WISHLIST_ABORT_CYCLE_KEYBOARD,
    ADD_TO_WISHLIST_ABORT_NO_CYCLE_KEYBOARD,
    ADD_TO_WISHLIST_ABORT_TOO_LONG_KEYBOARD,
    NEW_CUSTOM_CATEGORY_KEYBOARD,
    TOO_LONG_CUSTOM_CATEGORY_KEYBOARD,
    build_add_wishlist_element_category_keyboard,
    create_delete_all_wishlist_element_items_keyboard,
    create_wishlist_element_keyboard,
)
from root.contants.messages import (
    ADD_CATEGORY_TO_WISHLIST_ITEM_MESSAGE,
    ADD_LINK_TO_WISHLIST_ITEM_MESSAGE,
    ADD_NEW_LINK_MESSAGE_NUMBER_OF_NEW_PHOTOS,
    ADD_TO_WISHLIST_ACTIVATE_CYCLE_INSERT_APPEND,
    ADD_TO_WISHLIST_DEACTIVATE_CYCLE_INSERT_APPEND,
    ADD_TO_WISHLIST_MAX_PHOTOS_PROMPT,
    ADD_TO_WISHLIST_PROMPT,
    ADD_TO_WISHLIST_START_PROMPT,
    ADDED_TO_WISHLIST,
    CATEGORY_NAME_TOO_LONG,
    CATEGORY_NAME_TOO_LONG_WITH_EMOJI,
    CATEGORY_NAME_TOO_LONG_WITHOUT_EMOJI,
    CYCLE_INSERT_ENABLED_APPEND,
    DELETE_ALL_WISHLIST_ITEMS_AND_LIST_MESSAGE,
    DELETE_ALL_WISHLIST_ITEMS_MESSAGE,
    DELETE_ALL_WISHLIST_ITEMS_NO_PHOTO_MESSAGE,
    DELETE_WISHLIST_ITEMS_AND_PHOTOS_APPEND,
    DELETE_WISHLIST_ITEMS_APPEND,
    EDIT_WISHLIST_LINK_NO_PHOTOS,
    NEW_CATEGORY_MESSAGE,
    NO_CATEGORY_NAME_FOUND,
    NO_ELEMENT_IN_WISHLIST,
    NO_EMOJI_FOUND,
    NOTIFICATION_CREATED_ITEM_LINK_APPEND,
    NOTIFICATION_CREATED_ITEM_MESSAGE,
    NOTIFICATION_CREATED_ITEM_PHOTOS_APPEND,
    NOTIFICATION_DELETED_WISHLIST,
    NOTIFICATION_DELETED_WISHLIST_NO_ELEMENTS,
    NOTIFICATION_WIPED_WISHLIST_ELEMENTS,
    NOTIFICATION_WISHLIST_CHANGED,
    SUPPORTED_LINKS_MESSAGE,
    TOO_LONG_NEW_CATEGORY_MESSAGE,
    WISHLIST_DESCRIPTION_TOO_LONG,
    WISHLIST_ELEMENT_PRICE_OUTDATED_WARNING,
    WISHLIST_HEADER,
    WISHLIST_LEGEND_APPEND_FIRST_PAGE,
    WISHLIST_LEGEND_APPEND_LEGEND,
    WISHLIST_LEGEND_APPEND_SECOND_PAGE,
    WISHLIST_LEGEND_APPEND_SECOND_PAGE_ONLY,
    WISHLIST_LEGEND_APPEND_THIRD_PAGE,
    WISHLIST_LEGEND_APPEND_THIRD_PAGE_ONLY,
    WISHLIST_STEP_ONE,
    WISHLIST_STEP_THREE,
    WISHLIST_STEP_TWO,
    YOU_ARE_CREATING_A_NEW_CATEGORY,
    YOU_ARE_MODIFYING_THIS_ELEMENT,
)
from root.handlers.handlers import extractor
from root.helper import wishlist_element
from root.helper.custom_category_helper import (
    create_category_for_user,
    find_categories_for_user,
    find_category_for_user_by_description,
    find_category_for_user_by_id,
)
from root.helper.notification import create_notification
from root.helper.process_helper import find_process
from root.helper.subscriber_helper import find_subscriber
from root.helper.tracked_link_helper import (
    find_link_by_code,
    find_link_by_link,
    remove_tracked_subscriber,
)
from root.helper.user_helper import (
    create_user,
    get_current_wishlist_id,
    retrieve_user,
    user_exists,
)
from root.helper.wishlist import (
    count_all_wishlists_for_user,
    create_wishlist_if_empty,
    find_default_wishlist,
    find_wishlist_by_id,
)
from root.helper.wishlist_element import (
    count_all_wishlist_elements_for_user,
    count_all_wishlist_elements_for_wishlist_id,
    count_all_wishlist_elements_photos,
    delete_all_wishlist_element_for_user,
    find_containing_link,
    find_wishlist_element_by_id,
    find_wishlist_element_for_user,
    get_total_wishlist_element_pages_for_user,
    remove_wishlist_element_item_for_user,
    update_category_of_elements,
)
from root.manager.command_redirect import command_redirect
from root.manager.view_other_wishlists import view_other_wishlists
from root.model.custom_category import CustomCategory
from root.model.tracked_link import TrackedLink
from root.model.wishlist import Wishlist
from root.model.wishlist_element import WishlistElement
from root.util.telegram import TelegramSender
from root.util.util import (
    create_button,
    extract_first_link_from_message,
    format_deal_due_date,
    format_price,
    get_article,
    max_length_error_format,
)
from telegram import Update, message
from telegram.chat import Chat
from telegram.error import BadRequest
from telegram.ext import CallbackContext
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.ext.conversationhandler import ConversationHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram.files.inputmedia import InputMediaPhoto
from telegram.files.photosize import PhotoSize
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.message import Message
from telegram.user import User
from telegram_utils.utils.tutils import delete_if_private

sender = TelegramSender()

# endregion

INSERT_ITEM_IN_WISHLIST, INSERT_ZELDA, ADD_CATEGORY, CREATE_CATEGORY = range(4)

MAX_LINK_LENGTH = 27
MAX_CATEGORY_LENGTH = 15


def cycle_enabled(user: User):
    cycle_insert = redis_helper.retrieve("%s_cycle_insert" % user.id)
    if cycle_insert:
        logger.info("THE CYCLE INSERT IS AVAILABLE")
        if len(cycle_insert) > 0:
            cycle_insert = eval(cycle_insert.decode())
            return cycle_insert
        return False
    return False


def retrieve_photos_append(user: User, links: List[str] = None):
    rphotos: List[str] = redis_helper.retrieve("%s_%s_photos" % (user.id, user.id))
    if links:
        links = [link for link in links if not "🚫" in link]
    rphotos = eval(rphotos.decode()) if rphotos else []
    if len(rphotos) > 0:
        if not links:
            append = "   (<code>%s</code> / 10  foto)" % len(rphotos)
        else:
            append = "   (<code>%s</code> / 10  foto  •  <code>%s</code> / 10 link)" % (
                len(rphotos),
                len(links),
            )
    else:
        if not links:
            append = ""
        else:
            append = "   (<code>%s</code> / 10 link)" % len(links)
    return append


def show_new_line(price: str, has_media: bool):
    return "  •  "
    # if has_media and price:
    #    return "\n"
    # else:
    #    return "  •  "


def check_message_length(
    message_id: int,
    chat: Chat,
    message: str,
    context: CallbackContext,
    update: Update,
    user: User,
    wishlist_elements: List[WishlistElement],
    is_photo: bool = False,
    wishlist_element: WishlistElement = None,
    links: List[str] = None,
    pictures: List[str] = None,
):
    if cycle_enabled(user):
        cycle_append = ADD_TO_WISHLIST_DEACTIVATE_CYCLE_INSERT_APPEND
    else:
        cycle_append = ADD_TO_WISHLIST_ACTIVATE_CYCLE_INSERT_APPEND
    if len(message) > 128:
        logger.info("MESSAGE EXCEED 128 CHARACTERS")
        rphotos: List[str] = redis_helper.retrieve("%s_%s_photos" % (user.id, user.id))
        if rphotos:
            logger.info("PHOTOS HAS BEEN FOUND")
            rphotos = eval(rphotos.decode())
        else:
            logger.info("NO PHOTOS HAS BEEN FOUND")
            rphotos = []
        redis_helper.save(
            "%s_stored_wishlist_element" % user.id, update.effective_message.text[:128]
        )
        user_text = max_length_error_format(update.effective_message.text, 128, 200)
        wishlist_id = get_current_wishlist_id(user.id)
        wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
        title = f"{wishlist.title.upper()}  –  "
        message = (
            f"{WISHLIST_HEADER % title}<b>1.</b>  {user_text}{retrieve_photos_append(user)}\n"
            f"{WISHLIST_DESCRIPTION_TOO_LONG}\n\n"
        )
        if wishlist_elements:
            logger.info("ELEMENTS FOUND, CREATING MESSAGE...")
            message += "\n".join(
                [
                    (
                        f"<b>{index + 2}.</b>  {wish.description}\n"
                        f"<i>{wish.category}</i>{has_media(wish)}{show_new_line('', has_media(wish))}<i>Aggiunto %s{wish.creation_date.strftime('%d/%m/%Y')}</i>\n"
                        % (get_article(wish.creation_date))
                    )
                    for index, wish in enumerate(wishlist_elements)
                ]
            )
            append = (
                ADD_TO_WISHLIST_PROMPT % (10 - len(rphotos), cycle_append)
                if len(rphotos) < 10
                else ADD_TO_WISHLIST_MAX_PHOTOS_PROMPT % cycle_append
            )
            message += "\n\n%s%s" % (WISHLIST_STEP_ONE, append)
        else:
            logger.info("NO ELEMENTS FOUND, CREATING MESSAGE...")
            append = (
                ADD_TO_WISHLIST_PROMPT % (10 - len(rphotos), cycle_append)
                if len(rphotos) < 10
                else ADD_TO_WISHLIST_MAX_PHOTOS_PROMPT % cycle_append
            )
            message += "\n%s%s" % (WISHLIST_STEP_ONE, append)
        if len(message) <= 128:
            keyboard = ADD_TO_WISHLIST_ABORT_NO_CYCLE_KEYBOARD
        else:
            keyboard = ADD_TO_WISHLIST_ABORT_TOO_LONG_KEYBOARD
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
        return True
    else:
        logger.info("MESSAGE LENGTH IS OK")
        if not is_photo:
            logger.info("NO PHOTO FROM THE USER")
            wishlist_elements = wishlist_elements[:5]
            wishlist_id = get_current_wishlist_id(user.id)
            if not wishlist_element:
                logger.info("WISHLIST ELEMENT MISSING, CREATING ONE...")
                wishlist_element = WishlistElement(
                    user_id=user.id, description=message, wishlist_id=wishlist_id
                ).save()
                if links:
                    logger.info("UPDATING ELEMENT LINKS")
                    redis_helper.save(
                        "%s_%s_duplicated_links" % (user.id, user.id), str([])
                    )
                    wishlist_element.links = links
                    wishlist_element.save()
            wishlist_id = get_current_wishlist_id(user.id)
            wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
            title = f"{wishlist.title.upper()}  –  "
            text = WISHLIST_HEADER % title
            links_append = ""
            wishlist_element.links.reverse()
            links = wishlist_element.links
            duplicated_links = eval(
                redis_helper.retrieve(
                    "%s_%s_duplicated_links" % (user.id, user.id)
                ).decode()
            )
            if links:
                logger.info("ELEMENT HAS LINKS")
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
                    if len(links) > 1:
                        links_append += f"      ├─  {wishlist_link}"
                    else:
                        links_append += f"      └─  {wishlist_link}"
                elif index == len(links) - 1:
                    links_append += f"\n      └─  {wishlist_link}"
                else:
                    links_append += f"\n      ├─  {wishlist_link}"
            if links:
                links_append += "\n"
            message = (
                f"{WISHLIST_HEADER % title}<b>1.  {message}</b>{retrieve_photos_append(user, wishlist_element.links)}\n{links_append}"
                "✍🏻  <i>Stai inserendo questo elemento</i>\n\n"
            )
            if wishlist_elements:
                logger.info("WISHLIST ELEMENTS PRESENT...")
                wishlist_elements = list(wishlist_elements)
                wishlist_elements = wishlist_elements[1:]
                message += "\n".join(
                    [
                        (
                            f"<b>{index + 2}.</b>  {wish.description}\n"
                            f"<i>{wish.category}</i>{has_media(wish)}{show_new_line('', has_media(wish))}<i>Aggiunto %s{wish.creation_date.strftime('%d/%m/%Y')}</i>\n"
                            % (get_article(wish.creation_date))
                        )
                        for index, wish in enumerate(wishlist_elements)
                    ]
                )
            if wishlist_elements:
                if len(wishlist_elements) > 1:
                    message += "\n"
                if len(wishlist_elements) == 1:
                    message += "\n"
            cycle_message = CYCLE_INSERT_ENABLED_APPEND if cycle_enabled(user) else ""
            append = ADD_LINK_TO_WISHLIST_ITEM_MESSAGE % EDIT_WISHLIST_LINK_NO_PHOTOS
            logger.info(append)
            message += f"\n{WISHLIST_STEP_TWO}{append}{cycle_message}"
            logger.info(message)
            if pictures:
                try:
                    if len(pictures) > 0:
                        logger.info("SUPPORTED LINKS")
                        message += ADD_NEW_LINK_MESSAGE_NUMBER_OF_NEW_PHOTOS % (
                            len(pictures),
                            "e" if len(pictures) > 1 else "a",
                        )
                except Exception:
                    pass
            try:
                context.bot.edit_message_text(
                    message_id=message_id,
                    chat_id=chat.id,
                    text=message,
                    reply_markup=ADD_LINK_TO_WISHLIST_ITEM
                    if len(wishlist_element.links) > 0
                    else ADD_LINK_TO_WISHLIST_ITEM_NO_LINK,
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                )
                return
            except BadRequest:
                pass
        else:
            logger.info("PHOTO FROM THE USER")
            wishlist_id = get_current_wishlist_id(user.id)
            wishlist_elements = find_wishlist_element_for_user(
                user.id, page_size=4, wishlist_id=wishlist_id
            )
            wishlist_id = get_current_wishlist_id(user.id)
            wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
            title = f"{wishlist.title.upper()}  –  "
            message = (
                f"{WISHLIST_HEADER % title}<b>1.</b>  . . . . . .{retrieve_photos_append(user)}\n"
                "✍🏻  <i>Stai inserendo questo elemento</i>\n\n"
            )
            rphotos: List[str] = redis_helper.retrieve(
                "%s_%s_photos" % (user.id, user.id)
            )
            if rphotos:
                rphotos = eval(rphotos.decode())
            else:
                rphotos = []
            if wishlist_elements:
                logger.info("ELEMENTS FOUND, CREATING MESSAGE...")
                message += "\n".join(
                    [
                        (
                            f"<b>{index + 2}.</b>  {wish.description}\n"
                            f"<i>{wish.category}</i>{has_media(wish)}{show_new_line('', has_media(wish))}<i>Aggiunto %s{wish.creation_date.strftime('%d/%m/%Y')}</i>\n"
                            % (get_article(wish.creation_date))
                        )
                        for index, wish in enumerate(wishlist_elements)
                    ]
                )
                append = (
                    ADD_TO_WISHLIST_PROMPT % (10 - len(rphotos), cycle_append)
                    if len(rphotos) < 10
                    else ADD_TO_WISHLIST_MAX_PHOTOS_PROMPT % cycle_append
                )
                message += "\n\n%s%s" % (WISHLIST_STEP_ONE, append)
            else:
                logger.info("NO ELEMENTS FOUND...")
                append = (
                    ADD_TO_WISHLIST_PROMPT % (10 - len(rphotos), cycle_append)
                    if len(rphotos) < 10
                    else ADD_TO_WISHLIST_MAX_PHOTOS_PROMPT % cycle_append
                )
                message += "\n%s%s" % (WISHLIST_STEP_ONE, append)
            if not cycle_enabled(update.effective_user):
                keyboard = ADD_TO_WISHLIST_ABORT_NO_CYCLE_KEYBOARD
            else:
                keyboard = ADD_TO_WISHLIST_ABORT_CYCLE_KEYBOARD
            context.bot.edit_message_text(
                chat_id=chat.id,
                message_id=message_id,
                text=message,
                reply_markup=keyboard,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
        return False


def has_photo(wishlist_element: WishlistElement):
    if wishlist_element.user_id == 84872221:
        return ""
    return "  •  🖼" if wishlist_element.photos else ""


def has_media(wishlist_element: WishlistElement):
    if wishlist_element.user_id == 84872221:
        return ""
    if wishlist_element.links:
        if wishlist_element.photos:
            return "  •  🖼 🔗"
        else:
            return "  •  🔗"
    elif wishlist_element.photos:
        return "  •  🖼"
    else:
        return ""


def has_link(wishlist_element: WishlistElement):
    if wishlist_element.user_id == 84872221:
        return ""
    return "  •  🔗" if wishlist_element.links else ""


def ask_delete_all_wishlist_elements(
    update: Update, context: CallbackContext, from_wishlist=False
):
    message: Message = update.effective_message
    user: User = update.effective_user
    chat: Chat = update.effective_chat
    page: str = update.callback_query.data.split("_")[-1]
    wishlist_id = update.callback_query.data.split("_")[-2]
    wishlist = find_wishlist_by_id(wishlist_id)
    wishlist_elements = count_all_wishlist_elements_for_user(user.id, wishlist_id)
    photos = count_all_wishlist_elements_photos(user.id, wishlist_id)
    only_elements = False
    if update.callback_query.data:
        if not from_wishlist:
            from_wishlist = "fw" in update.callback_query.data
        only_elements = "fw" in update.callback_query.data
    if from_wishlist:
        if photos:
            text = "(%s element%s, %s foto)" % (
                wishlist_elements,
                "o" if wishlist_elements == 1 else "i",
                photos,
            )
            append = DELETE_WISHLIST_ITEMS_AND_PHOTOS_APPEND
        elif wishlist_elements:
            text = "(%s element%s)" % (
                wishlist_elements,
                "o" if wishlist_elements == 1 else "i",
            )
            append = DELETE_WISHLIST_ITEMS_APPEND
        else:
            text = "(lista vuota)"
            append = ""
        if photos > 0:
            if not only_elements:
                text = DELETE_ALL_WISHLIST_ITEMS_AND_LIST_MESSAGE % (
                    "",
                    f"{wishlist.title}",
                    "\n",
                    text,
                    append,
                )
            else:
                text = DELETE_ALL_WISHLIST_ITEMS_MESSAGE % (
                    f"{wishlist.title.upper()}  –  ",
                    wishlist_elements,
                    "o" if wishlist_elements == 1 else "i",
                    photos,
                )
        else:
            if not only_elements:
                text = DELETE_ALL_WISHLIST_ITEMS_AND_LIST_MESSAGE % (
                    "",
                    f"{wishlist.title}",
                    "  ",
                    text,
                    append,
                )
            else:
                text = DELETE_ALL_WISHLIST_ITEMS_NO_PHOTO_MESSAGE % (
                    f"{wishlist.title.upper()}  –  ",
                    wishlist_elements,
                    "o" if wishlist_elements == 1 else "i",
                )
    else:
        if photos > 0:
            text = DELETE_ALL_WISHLIST_ITEMS_MESSAGE % (
                f"{wishlist.title.upper()}  –  ",
                wishlist_elements,
                "o" if wishlist_elements == 1 else "i",
                photos,
            )
        else:
            text = DELETE_ALL_WISHLIST_ITEMS_NO_PHOTO_MESSAGE % (
                f"{wishlist.title.upper()}  –  ",
                wishlist_elements,
                "o" if wishlist_elements == 1 else "i",
            )
    context.bot.edit_message_text(
        chat_id=chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=create_delete_all_wishlist_element_items_keyboard(
            page, from_wishlist, wishlist_id, only_elements
        ),
        disable_web_page_preview=True,
        parse_mode="HTML",
    )


def confirm_delete_all_wishlist_elements(
    update: Update, context: CallbackContext, from_wishlist=False
):
    user = update.effective_user
    data = update.callback_query.data
    wishlist_id = data.split("_")[-1]
    current_wishlist_id = get_current_wishlist_id(user.id)
    current_wishlist: Wishlist = find_wishlist_by_id(current_wishlist_id)
    wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
    elements = count_all_wishlist_elements_for_wishlist_id(wishlist_id, user.id)
    if elements == 1:
        char = "o"
    else:
        char = "i"
    if not "confirm_delete_wishlist_list" in update.callback_query.data:
        photos: int = count_all_wishlist_elements_photos(
            update.effective_user.id, str(wishlist.id)
        )
        logger.info("QUESTE SONO LE FOTO DELLA WISHLIST [%s]" % wishlist_id)
        if photos > 0:
            photos = ", %s foto" % photos
        else:
            photos = ""
        notification = NOTIFICATION_WIPED_WISHLIST_ELEMENTS % (
            wishlist.title,
            elements,
            photos,
            char,
        )
    else:
        photos: int = count_all_wishlist_elements_photos(
            update.effective_user.id, str(wishlist.id)
        )
        logger.info("QUESTE SONO LE FOTO DELLA WISHLIST [%s]" % wishlist_id)
        if photos > 0:
            photos = ", %s foto" % photos
        else:
            photos = ""
        count = count_all_wishlists_for_user(user_id=update.effective_user.id)
        count -= 1
        if elements > 0:
            notification = NOTIFICATION_DELETED_WISHLIST % (
                wishlist.title,
                elements,
                char,
                photos,
                count,
            )
        else:
            notification = NOTIFICATION_DELETED_WISHLIST_NO_ELEMENTS % (
                wishlist.title,
                count,
            )
    create_notification(user.id, notification)
    default_wishlist = find_default_wishlist(user.id)
    if str(current_wishlist.id) == str(wishlist.id):
        notification = NOTIFICATION_WISHLIST_CHANGED % (
            wishlist.title,
            default_wishlist.title,
        )
        create_notification(user.id, notification)
    delete_all_wishlist_element_for_user(
        update.effective_user.id, wishlist_id, from_wishlist
    )
    update.callback_query.data += "_0"
    if not from_wishlist:
        if update.callback_query:
            from_wishlist = "fw" in update.callback_query.data
    if not from_wishlist:
        view_wishlist(update, context, reset_keyboard=False)
    else:
        redis_helper.save(
            "%s_%s_new_wishlist" % (user.id, user.id),
            update.effective_message.message_id,
        )
        title = wishlist.title
        wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
        if not wishlist:
            append = f"✅  <i>Lista <b>{title}</b> eliminata!</i>"
        else:
            append = f"✅  <i>Lista <b>{title}</b> svuotata!</i>"
        view_other_wishlists(update, context, edit=True, append=append)


def abort_delete_all_wishlist_elements(update: Update, context: CallbackContext):
    from_wishlist = False
    if update.callback_query:
        from_wishlist = "fw" in update.callback_query.data
    if not from_wishlist:
        page: str = update.callback_query.data.split("_")[-1]
        view_wishlist(update, context, reset_keyboard=False)
    else:
        view_other_wishlists(update, context, edit=True)


def confirm_wishlist_element_deletion(update: Update, context: CallbackContext):
    user: User = update.effective_user
    chat: Chat = update.effective_chat
    if update.callback_query:
        context.bot.answer_callback_query(update.callback_query.id)
        _id = update.callback_query.data.split("_")[-1]
        page = int(update.callback_query.data.split("_")[-2])
        wishlist_element = find_wishlist_element_by_id(_id)
        remove_wishlist_element_item_for_user(_id)
        for link in wishlist_element.links:
            logger.info("removing %s" % link)
            remove_tracked_subscriber(extractor.extract_code(link), user.id)
        wishlist_id = get_current_wishlist_id(user.id)
        total_pages = get_total_wishlist_element_pages_for_user(
            user.id, wishlist_id=wishlist_id
        )
        if page + 1 > total_pages:
            page -= 1
        update.callback_query.data += "_%s" % page
    message_id = redis_helper.retrieve("%s_redis_message" % user.id).decode()
    if message_id:
        message_id = int(message_id)
        update.effective_message.message_id = message_id
    messages = redis_helper.retrieve("%s_photos_message" % user.id).decode()
    if messages:
        messages = eval(messages)
    else:
        messages = []
    for message_id in messages:
        try:
            context.bot.delete_message(chat_id=chat.id, message_id=message_id)
        except BadRequest:
            pass
    view_wishlist(update, context, reset_keyboard=True)


def remove_wishlist_element_item(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    message_id = message.message_id
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    if update.callback_query:
        context.bot.answer_callback_query(update.callback_query.id)
        _id = update.callback_query.data.split("_")[-1]
        page = int(update.callback_query.data.split("_")[-2])
        index = update.callback_query.data.split("_")[-3]
        keyboard = [
            [
                create_button(
                    "✅  Sì",
                    f"confirm_remove_wishlist_element_{page}_{_id}",
                    f"confirm_remove_wishlist_element_{page}_{_id}",
                ),
                create_button(
                    "❌  No",
                    f"cancel_remove_wishlist_element_{page}",
                    f"cancel_remove_wishlist_element_{page}",
                ),
            ]
        ]
        wish: WishlistElement = find_wishlist_element_by_id(_id)
        if wish.photos:
            try:
                context.bot.delete_message(chat_id=chat.id, message_id=message_id)
            except BadRequest:
                logger.info("Unable to delete the message")
        if not wish.photos:
            wishlist_id = get_current_wishlist_id(user.id)
            wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
            title = f"{wishlist.title.upper()}  –  "
            text = WISHLIST_HEADER % title
        else:
            text = ""
        append = "🚮  <i>Stai per cancellare questo elemento</i>"
        if wish:
            if wish.photos:
                append += "<i> e <b>%s</b> foto</i>" % len(wish.photos)
        if not wish:
            update.callback_query.data += "_%s" % page
            view_wishlist(update, context, reset_keyboard=False)
            return
        text += f"<b>{index}</b>  <b>{wish.description}</b>     (<i>{wish.category}</i>)\n{append}\n\n"
        text += "<b>Vuoi confermare?</b>"
        keyboard = InlineKeyboardMarkup(keyboard)
        photos: List = wish.photos
        photos = [InputMediaPhoto(media=photo) for photo in photos]
        if len(photos) > 1:
            message: List[Message] = context.bot.send_media_group(
                chat_id=chat.id, media=photos
            )
            message = [m.message_id for m in message]
        elif len(photos) == 1:
            message: Message = context.bot.send_photo(
                chat_id=chat.id, photo=photos[0].media
            )
            message = [message.message_id]
        else:
            message = []
        redis_helper.save("%s_photos_message" % user.id, str(message))
        if wish.photos:
            message: Message = context.bot.send_message(
                chat_id=chat.id,
                text=text,
                reply_markup=keyboard,
                disable_web_page_preview=True,
                parse_mode="HTML",
            )
        else:
            message: Message = context.bot.edit_message_text(
                chat_id=chat.id,
                message_id=message_id,
                text=text,
                reply_markup=keyboard,
                disable_web_page_preview=True,
                parse_mode="HTML",
            )
        message_id: int = message.message_id
        redis_helper.save("%s_redis_message" % user.id, message_id)


def abort_delete_item_wishlist_element(update: Update, context: CallbackContext):
    user: User = update.effective_user
    chat: Chat = update.effective_chat
    message_id = redis_helper.retrieve("%s_redis_message" % user.id).decode()
    if message_id:
        message_id = int(message_id)
        update.effective_message.message_id = message_id
    messages = redis_helper.retrieve("%s_photos_message" % user.id).decode()
    if messages:
        messages = eval(messages)
    else:
        messages = []
    for message_id in messages:
        try:
            context.bot.delete_message(chat_id=chat.id, message_id=message_id)
        except BadRequest:
            pass
    view_wishlist(update, context, reset_keyboard=False)


def view_wishlist(
    update: Update,
    context: CallbackContext,
    append: str = None,
    page: int = None,
    under_first: bool = True,
    reset_keyboard: bool = True,
):
    if not update.effective_message.chat.type == "private":
        command_redirect("wishlist", "wishlist", update, context)
        return
    has_tracked_links = False
    message: Message = update.effective_message
    message_id = message.message_id
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    redis_helper.save("%s_%s_on_list" % (user.id, user.id), "0")
    if not user_exists(user.id):
        create_user(user)
    create_wishlist_if_empty(user.id)
    wishlist_id = get_current_wishlist_id(user.id)
    if update.callback_query:
        if "noreset" in update.callback_query.data:
            reset_keyboard = False
    if reset_keyboard:
        reset_redis_wishlist_keyboard(
            user.id,
            count_all_wishlist_elements_for_wishlist_id(wishlist_id, user.id),
        )
    try:
        if not update.callback_query:
            sender.delete_if_private(context, message)
    except Exception:
        pass
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
            page = int(update.callback_query.data.split("_")[-1])
        else:
            page = 0
    else:
        page = int(page)
        message_id = redis_helper.retrieve(user.id).decode()
    total_pages = get_total_wishlist_element_pages_for_user(
        user.id, wishlist_id=wishlist_id
    )
    wishlist_id = get_current_wishlist_id(user.id)
    wishlist_elements = find_wishlist_element_for_user(
        user.id, page, wishlist_id=wishlist_id
    )

    chat: Chat = update.effective_chat
    if chat.type != "private":
        # ignore all requests coming outside a private chat
        return ConversationHandler.END
    if wishlist_elements:
        message = ""
        if append and under_first:
            inc = 1
            wishlist_elements = list(wishlist_elements)
            wish: WishlistElement = wishlist_elements[0]
            logger.info(wishlist_elements[0].photos)
            wishlist_elements.remove(wish)
            if len(wishlist_elements) == 0:
                new_line = ""
            else:
                new_line = "\n\n"
            message += f"<b>1.</b>  {wish.description}{append}{new_line}"
        else:
            inc = 0
        msgs = []
        if wishlist_elements:
            wishlist_elements = list(wishlist_elements)
            wish = wishlist_elements[-1]
            last = str(((wishlist_elements.index(wish)) + (5 * page + 1)) + inc)
            wish = wishlist_elements[0]
            first = str(0 + (5 * page + 1) + inc)
            add_space = len(last) > len(first)
        else:
            add_space = False
        for index, wish in enumerate(wishlist_elements):
            index = ((index) + (5 * page + 1)) + inc
            if index == int(last):
                space = ""
                new_line = ""
            else:
                space = "  " if add_space else ""
                new_line = "\n"
            price = ""
            if wish.links:
                link = ""
                for l in wish.links:
                    if extractor.is_supported(l):
                        link = l
                tracked_link: TrackedLink = find_link_by_link(link)
                if tracked_link:
                    has_tracked_links = True
                    if tracked_link.price > 0:
                        if not tracked_link.collect_available:
                            tracked_link.price = (
                                tracked_link.price
                                + extractor.get_shipment_cost(
                                    tracked_link.price, tracked_link.link
                                )
                            )
                        if tracked_link.deals_end:
                            append = format_deal_due_date(
                                tracked_link.deals_end, datetime.now()
                            )
                        else:
                            append = ""
                        price = "<b>%s €%s ⁽*⁾</b>\n" % (
                            format_price(tracked_link.price),
                            append,
                        )
                    else:
                        price = "<b>N/D ⁽*⁾</b>\n"

            msgs.append(
                f"<b>{space}{index}.</b>  {wish.description}\n"
                f"{price}<i>{wish.category}</i>{has_media(wish)}{show_new_line(price, has_media(wish))}<i>Aggiunto %s{wish.creation_date.strftime('%d/%m/%Y')}</i>{new_line}"
                % (get_article(wish.creation_date))
            )
        message += "\n".join(msgs)
        if append and under_first:
            wishlist_elements.insert(0, wish)
    else:
        inc = 0
        message = NO_ELEMENT_IN_WISHLIST
    wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
    title = f"{wishlist.title.upper()}  –  "
    if total_pages > 1:
        more_pages_append = (
            f"🧮  <i>Questa lista dei desideri contiene <b>%s</b> elementi.</i>\n\n"
            % count_all_wishlist_elements_for_wishlist_id(wishlist_id, user.id)
        )
    else:
        more_pages_append = ""
    message = "%s%s%s" % (WISHLIST_HEADER % title, more_pages_append, message)
    first_page = page + 1 == 1
    last_page = page + 1 == total_pages
    total_wishlists = count_all_wishlists_for_user(user.id)
    if has_tracked_links:
        message += WISHLIST_ELEMENT_PRICE_OUTDATED_WARNING
    # #############################################################################
    if len(list(wishlist_elements)) > 0:
        message += WISHLIST_LEGEND_APPEND_LEGEND

    if not reset_keyboard:
        first_page_added = False
        second_page_added = False
        third_page_added = False
        append_legend = []
        extra_spaces = ""
        for index in range(1, len(wishlist_elements) + 1):
            element = redis_helper.retrieve(
                "%s_element_page_%s." % (user.id, index + (5 * page))
            ).decode()
            logger.info("THE CURRENT VIEW PAGE IS %s" % element)
            if element == "2":
                if not second_page_added:
                    if len(list(wishlist_elements)) > 0:
                        if third_page_added:
                            if first_page_added:
                                append_legend.insert(
                                    1, WISHLIST_LEGEND_APPEND_SECOND_PAGE
                                )
                            else:
                                append_legend.insert(
                                    0, WISHLIST_LEGEND_APPEND_SECOND_PAGE
                                )
                        else:
                            append_legend.append(WISHLIST_LEGEND_APPEND_SECOND_PAGE)
                        second_page_added = True
                extra_spaces += "&#8203;"
            elif element == "1":
                if not first_page_added:
                    if len(list(wishlist_elements)) > 0:
                        append_legend.insert(0, WISHLIST_LEGEND_APPEND_FIRST_PAGE)
                        first_page_added = True
            elif element == "3":
                if not third_page_added:
                    if len(list(wishlist_elements)) > 0:
                        third_page_added = True
                        append_legend.append(WISHLIST_LEGEND_APPEND_THIRD_PAGE)
        if not first_page_added:
            for index, value in enumerate(append_legend):
                if value == WISHLIST_LEGEND_APPEND_SECOND_PAGE:
                    append_legend[index] = WISHLIST_LEGEND_APPEND_SECOND_PAGE_ONLY
                if value == WISHLIST_LEGEND_APPEND_THIRD_PAGE:
                    append_legend[index] = WISHLIST_LEGEND_APPEND_THIRD_PAGE_ONLY
        if len(append_legend) == 1:
            if append_legend[0] == WISHLIST_LEGEND_APPEND_SECOND_PAGE:
                message += WISHLIST_LEGEND_APPEND_SECOND_PAGE_ONLY
            elif append_legend[0] == WISHLIST_LEGEND_APPEND_THIRD_PAGE:
                message += WISHLIST_LEGEND_APPEND_THIRD_PAGE_ONLY
            else:
                append_legend = "".join(append_legend)
                message += append_legend
        else:
            append_legend = "".join(append_legend)
            message += append_legend
        message += extra_spaces
    else:
        if len(list(wishlist_elements)) > 0:
            message += WISHLIST_LEGEND_APPEND_FIRST_PAGE
    wishlist_elements = find_wishlist_element_for_user(
        user.id, page, wishlist_id=wishlist_id
    )
    wishlist_elements = list(wishlist_elements)
    if not under_first and append:
        if len(wishlist_elements) > 0:
            message += f"\n\n{append}"
        else:
            message += f"\n\n\n{append}"
    if update.callback_query:
        try:
            context.bot.edit_message_text(
                chat_id=chat.id,
                message_id=message_id,
                text=message,
                reply_markup=create_wishlist_element_keyboard(
                    page,
                    total_pages,
                    wishlist_elements,
                    first_page,
                    last_page,
                    inc,
                    total_wishlists,
                    user.id,
                ),
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
        except BadRequest:
            try:
                context.bot.edit_message_text(
                    chat_id=chat.id,
                    message_id=update.effective_message.message_id,
                    text=message,
                    reply_markup=create_wishlist_element_keyboard(
                        page,
                        total_pages,
                        wishlist_elements,
                        first_page,
                        last_page,
                        inc,
                        total_wishlists,
                        user.id,
                    ),
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                )
            except BadRequest:
                pass
    else:
        context.bot.send_message(
            chat_id=chat.id,
            text=message,
            reply_markup=create_wishlist_element_keyboard(
                page,
                total_pages,
                wishlist_elements,
                first_page,
                last_page,
                inc,
                total_wishlists,
                user.id,
            ),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )


def clear_redis(user: User, toggle_cycle: bool = False):
    redis_helper.save("%s_stored_wishlist_element" % user.id, "")
    if not toggle_cycle:
        redis_helper.save("%s_%s_photos" % (user.id, user.id), "")
        redis_helper.save("%s_cycle_insert" % user.id, str(False))


def add_in_wishlist_element(
    update: Update,
    context: CallbackContext,
    cycle_insert: bool = False,
    toggle_cycle: bool = False,
):
    if not cycle_insert:
        cycle_append = ADD_TO_WISHLIST_ACTIVATE_CYCLE_INSERT_APPEND
    else:
        cycle_append = ADD_TO_WISHLIST_DEACTIVATE_CYCLE_INSERT_APPEND
    message: Message = update.effective_message
    user: User = update.effective_user
    message_id = message.message_id
    clear_redis(user, toggle_cycle)
    rphotos = []
    redis_helper.save("%s_%s_duplicated_links" % (user.id, user.id), str([]))
    if update.callback_query:
        context.bot.answer_callback_query(update.callback_query.id)
    chat: Chat = update.effective_chat
    if chat.type != "private":
        # ignore all requests coming outside a private chat
        return ConversationHandler.END
    redis_helper.save(user.id, message.message_id)
    wishlist_id = get_current_wishlist_id(user.id)
    wishlist_elements = find_wishlist_element_for_user(
        user.id, page_size=4, wishlist_id=wishlist_id
    )
    wishlist_id = get_current_wishlist_id(user.id)
    wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
    title = f"{wishlist.title.upper()}  –  "
    append = retrieve_photos_append(user, None)
    message = (
        f"{WISHLIST_HEADER % title}<b>1.</b>  . . . . . .{append}\n"
        "✍🏻  <i>Stai inserendo questo elemento</i>\n\n"
    )
    logger.info("STO PASSANDO DI QUI")
    rphotos: List[str] = redis_helper.retrieve("%s_%s_photos" % (user.id, user.id))
    rphotos = eval(rphotos.decode()) if rphotos else []
    if len(rphotos) > 0:
        if len(rphotos) < 10:
            append = ADD_TO_WISHLIST_PROMPT % (10 - len(rphotos), cycle_append)
        else:
            append = ADD_TO_WISHLIST_MAX_PHOTOS_PROMPT % cycle_append
    else:
        append = ADD_TO_WISHLIST_START_PROMPT % cycle_append
    logger.info(append)
    if wishlist_elements:
        message += "\n".join(
            [
                (
                    f"<b>{index + 2}.</b>  {wish.description}\n"
                    f"<i>{wish.category}</i>{has_media(wish)}{show_new_line('', has_media(wish))}<i>Aggiunto %s{wish.creation_date.strftime('%d/%m/%Y')}</i>\n"
                    % (get_article(wish.creation_date))
                )
                for index, wish in enumerate(wishlist_elements)
            ]
        )
        message += "\n\n%s%s" % (WISHLIST_STEP_ONE, append)
    else:
        message += "\n%s%s" % (WISHLIST_STEP_ONE, append)
    try:
        logger.info("THE CYCLE INSERT VALUE IS [%s]" % cycle_insert)
        context.bot.edit_message_text(
            chat_id=chat.id,
            message_id=message_id,
            text=message,
            reply_markup=ADD_TO_WISHLIST_ABORT_NO_CYCLE_KEYBOARD
            if not cycle_insert
            else ADD_TO_WISHLIST_ABORT_CYCLE_KEYBOARD,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except BadRequest:
        pass
    return INSERT_ITEM_IN_WISHLIST


def handle_add_confirm(
    update: Update, context: CallbackContext, links: List[str] = None
):
    message: Message = update.effective_message
    message_id: int = message.message_id
    user: User = update.effective_user
    chat: Chat = update.effective_chat
    if not update.callback_query:
        message: str = message.text if message.text else message.caption
        message: str = message.strip()
        message: str = message.split("\n")[0]
        message: str = re.sub(r"\s{2,}", " ", message)
        redis_helper.save("%s_stored_wishlist_element" % user.id, message)
    else:
        message = redis_helper.retrieve("%s_stored_wishlist_element" % user.id)
        message = message.decode()
    if chat.type != "private":
        # ignore all requests coming outside a private chat
        return ConversationHandler.END
    # delete the user message
    if not update.callback_query:
        context.bot.delete_message(chat_id=chat.id, message_id=message_id)
    overload = False
    message_id = redis_helper.retrieve(user.id).decode()
    wishlist_id = get_current_wishlist_id(user.id)
    wishlists_element = find_wishlist_element_for_user(
        user.id, page_size=4, wishlist_id=wishlist_id
    )
    overload = check_message_length(
        message_id, chat, message, context, update, user, wishlists_element, links=links
    )
    return INSERT_ZELDA if not overload else INSERT_ITEM_IN_WISHLIST


def add_category(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    user: User = update.effective_user
    context.bot.answer_callback_query(update.callback_query.id)
    data = update.callback_query.data
    wishlist_id = get_current_wishlist_id(user.id)
    wish: WishlistElement = find_wishlist_element_for_user(
        user.id, 0, 1, wishlist_id=wishlist_id
    )
    rphotos: List[str] = redis_helper.retrieve("%s_%s_photos" % (user.id, user.id))
    rphotos = eval(rphotos.decode()) if rphotos else []
    if wish:
        wish = wish[0]
        if not "custom" in data:
            category = int(data.split("_")[-1])
            wish.category = CATEGORIES[category]
        else:
            _id = data.split("_")[-1]
            category: CustomCategory = find_category_for_user_by_id(
                update.effective_user.id, _id
            )
            if category:
                wish.category = category.description
            else:
                wish.category = CATEGORIES[0]
        wish.photos = rphotos
        user = retrieve_user(user.id)
        if user:
            wish.wishlist_id = user.current_wishlist
        for link in wish.links:
            try:
                if "www." in link:
                    link = re.sub("www\.", "", link)
                product = extractor.parse_url(link)
                logger.info(product)
                extractor.add_subscriber(link, user.user_id, product)
            except ValueError as e:
                logger.error(e)
        links = []
        tracked_links = []
        for link in wish.links:
            if extractor.is_supported(link):
                code = extractor.extract_code(link)
                tracked_link: TrackedLink = find_link_by_code(code)
                tracked_links.append(tracked_link)
            else:
                links.insert(0, link)
        tracked_links.sort(key=lambda link: link.price, reverse=True)
        [links.insert(0, link.link) for link in tracked_links]
        links.reverse()
        wish.links = links
        wish.save()
        cycle_insert = redis_helper.retrieve("%s_cycle_insert" % user.user_id)
        logger.info("THE CYCLE INSERT VALUE IS [%s]" % cycle_insert)
        if cycle_insert:
            logger.info("THE CYCLE INSERT IS AVAILABLE")
            reset_redis_wishlist_keyboard(
                user.user_id,
                count_all_wishlist_elements_for_wishlist_id(wishlist_id, user.user_id),
            )
            wishlist: Wishlist = find_wishlist_by_id(wish.wishlist_id)
            element_extra = []
            format_text = [wish.description]
            if wish.photos:
                element_extra.append(
                    NOTIFICATION_CREATED_ITEM_PHOTOS_APPEND % len(wish.photos)
                )
            if wish.links:
                element_extra.append(
                    NOTIFICATION_CREATED_ITEM_LINK_APPEND % len(wish.links)
                )
                for link in wish.links:
                    if len(link) >= MAX_LINK_LENGTH:
                        link = '        •  <a href="%s">%s...</a>' % (
                            link,
                            link[: MAX_LINK_LENGTH - 3],
                        )
                    else:
                        link = '        •  <a href="%s">%s</a>' % (link, link)
                    element_extra.append(link)
            if element_extra:
                element_extra = "\n%s\n" % "\n".join(element_extra)
                # if wish.photos:
                #    if wish.links:
                #        element = [element_extra[0], element_extra[1]]
                #        element_extra = element_extra[2:]
                #        element_extra = "\n".join(element_extra)
                #        element = " (%s)" % ", ".join(element)
                #        element_extra = " (%s%s)" % (element, element_extra)
                #    else:
                #        element_extra = " (%s)" % element_extra[0]
                # else:
                #    element_extra = " (%s)" % "\n".join(element_extra)
            else:
                element_extra = ""
            format_text.append(wish.category)
            format_text.append(element_extra)
            format_text.append(wishlist.title)
            notification_message = NOTIFICATION_CREATED_ITEM_MESSAGE % tuple(
                format_text
            )

            create_notification(user.user_id, notification_message)
            if len(cycle_insert) > 0:
                cycle_insert = eval(cycle_insert.decode())
                if cycle_insert:
                    redis_helper.save(
                        "%s_%s_photos"
                        % (update.effective_user.id, update.effective_user.id),
                        "",
                    )
                    add_in_wishlist_element(update, context, cycle_insert, cycle_insert)
                    return INSERT_ITEM_IN_WISHLIST
        view_wishlist(update, context, ADDED_TO_WISHLIST, "0", reset_keyboard=True)
        return ConversationHandler.END


def cancel_add_in_wishlist_element(update: Update, context: CallbackContext):
    data = update.callback_query.data
    user: User = update.effective_user
    if not "NO_DELETE" in data:
        wishlist_id = get_current_wishlist_id(user.id)
        wish: WishlistElement = find_wishlist_element_for_user(
            user.id, 0, 1, wishlist_id=wishlist_id
        )
        if wish:
            wish = wish[0]
            wish.delete()
    update.callback_query.data += "_0"
    redis_helper.save("%s_%s_photos" % (user.id, user.id), "")
    view_wishlist(update, context, reset_keyboard=False)
    return ConversationHandler.END


def handle_insert_for_link(
    update: Update, context: CallbackContext, from_call: bool = False
):
    message: Message = update.effective_message
    chat: Chat = update.effective_chat
    user = update.effective_user
    wishlist_id = get_current_wishlist_id(user.id)
    if not update.callback_query:
        context.bot.delete_message(chat_id=chat.id, message_id=message.message_id)
        wishlist_id = get_current_wishlist_id(user.id)
        wishlist_element: WishlistElement = find_wishlist_element_for_user(
            user.id, 0, 1, wishlist_id=wishlist_id
        )
        if wishlist_element:
            wishlist_element = wishlist_element[0]
            wishlist_link = message.text if message.text else message.caption
            pictures = extractor.load_url(wishlist_link)
            pictures = pictures[:10]
            rphotos: List[str] = redis_helper.retrieve(
                "%s_%s_photos" % (user.id, user.id)
            )
            if rphotos:
                rphotos = eval(rphotos.decode())
            else:
                rphotos = []
            if len(pictures) > 0:
                total_left = 10 - len(rphotos)
                pictures = pictures[:total_left]
                rphotos = rphotos + pictures
                rphotos = rphotos[-1] if len(rphotos) > 10 else rphotos
                redis_helper.save("%s_%s_photos" % (user.id, user.id), str(rphotos))
            duplicated_links = eval(
                redis_helper.retrieve(
                    "%s_%s_duplicated_links" % (user.id, user.id)
                ).decode()
            )
            if not from_call:
                wishlist_link = extract_first_link_from_message(
                    update.effective_message
                )
                if "/" in wishlist_link:
                    link = wishlist_link
                    link = re.sub(r".*//", "", link)
                    link = link.split("/")
                    link[0] = link[0].lower()
                    wishlist_link = "/".join(link)
                    # wishlist_element.links = "/".join(link)
                is_present = False
                for link in wishlist_element.links:
                    if not is_present:
                        is_present = (
                            SequenceMatcher(None, wishlist_link, link).ratio() > 0.9
                        )
                        duplicated_type = "DUPLICATO"
                if not is_present:
                    is_present = extractor.domain_duplicated(
                        wishlist_link, wishlist_element.links
                    )
                    duplicated_type = "DOMINIO WEB DUPLICATO"
                if not is_present:
                    is_present = (
                        True
                        if find_subscriber(
                            user.id, extractor.extract_code(wishlist_link)
                        )
                        else False
                    )
                    duplicated_type = "DUPLICATO IN UN ALTRO ELEMENTO"
                if is_present:
                    if len(wishlist_link) > MAX_LINK_LENGTH:
                        wishlist_link = '<a href="%s">%s...</a>' % (
                            wishlist_link,
                            wishlist_link[:MAX_LINK_LENGTH],
                        )
                    duplicated_link = "<s>%s</s>     🚫 <b>%s</b>" % (
                        wishlist_link,
                        duplicated_type,
                    )
                    if len(duplicated_links) == 10:
                        duplicated_links.pop()
                    duplicated_links.insert(0, duplicated_link)
                    redis_helper.save(
                        "%s_%s_duplicated_links" % (user.id, user.id),
                        str(duplicated_links),
                    )
                if not is_present:
                    wishlist_element.links.append(wishlist_link)
                wishlist_element.wishlist_id = wishlist_id
                wishlist_element.save()
    message_id = redis_helper.retrieve(user.id).decode()
    wishlist_elements = find_wishlist_element_for_user(
        user.id, page_size=5, wishlist_id=wishlist_id
    )
    wishlist_element = wishlist_elements[0]
    wishlist_elements = wishlist_elements[1:5]
    wishlist_id = get_current_wishlist_id(user.id)
    wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
    title = f"{wishlist.title.upper()}  –  "
    links = wishlist_element.links
    message = (
        f"{WISHLIST_HEADER % title}<b>1.  {wishlist_element.description}</b>{retrieve_photos_append(user, links)}\n"
        "✍🏻  <i>Stai inserendo questo elemento</i>\n\n"
    )
    cycle_message = CYCLE_INSERT_ENABLED_APPEND if cycle_enabled(user) else ""
    if wishlist_elements:
        article = "il"
        message += "\n".join(
            [
                (
                    f"<b>{index + 2}.</b>  {wish.description}\n"
                    f"<i>{wish.category}</i>{has_media(wish)}{show_new_line('', has_media(wish))}<i>Aggiunto %s{wish.creation_date.strftime('%d/%m/%Y')}</i>\n"
                    % (get_article(wish.creation_date))
                )
                for index, wish in enumerate(wishlist_elements)
            ]
        )
        message += "\n\n%s%s%s" % (
            WISHLIST_STEP_THREE,
            ADD_CATEGORY_TO_WISHLIST_ITEM_MESSAGE,
            cycle_message,
        )
    else:
        message += "\n%s%s%s" % (
            WISHLIST_STEP_THREE,
            ADD_CATEGORY_TO_WISHLIST_ITEM_MESSAGE,
            cycle_message,
        )
    if not update.callback_query and not from_call:
        if len(wishlist_element.links) < 10:
            message = check_message_length(
                message_id,
                chat,
                wishlist_element.description,
                context,
                update,
                user,
                wishlist_elements,
                False,
                wishlist_element,
                pictures=pictures,
            )
            return INSERT_ZELDA
    categories: List[CustomCategory] = find_categories_for_user(
        user_id=update.effective_user.id
    )
    context.bot.edit_message_text(
        message_id=message_id,
        chat_id=chat.id,
        text=message,
        reply_markup=build_add_wishlist_element_category_keyboard(
            wishlist_id, categories
        ),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
    return ADD_CATEGORY


def reset_redis_wishlist_keyboard(user_id: int, total_elements: int):
    for index in range(0, total_elements + 1):
        redis_helper.save("%s_element_page_%s." % (user_id, index), "1")


def toggle_element_action_page(update: Update, context: CallbackContext):
    user: User = update.effective_user
    index = update.callback_query.data.split("_")[-3]
    element_page = redis_helper.retrieve("%s_element_page_%s" % (user.id, index))
    logger.info("THE CURRENT PAGE IS %s" % element_page)
    if element_page:
        element_page = eval(element_page.decode())
        if element_page == 0:
            element_page = 1
    else:
        element_page = 1
    if "next" in update.callback_query.data:
        element_page += 1
    else:
        element_page -= 1
    logger.info("THE NEW PAGE IS %s" % element_page)
    redis_helper.save("%s_element_page_%s" % (user.id, index), str(element_page))

    view_wishlist(update, context, reset_keyboard=False)


def extract_photo_from_message(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    delete_if_private(message)
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    photo: List[PhotoSize] = message.photo
    if photo:
        photo: PhotoSize = max(photo, key=operator.attrgetter("file_size"))
        photo: str = photo.file_id
    if not photo:
        if message.document:
            photo: str = message.document.file_id
    rphotos: List[str] = redis_helper.retrieve("%s_%s_photos" % (user.id, user.id))
    if rphotos:
        rphotos = eval(rphotos.decode())
    else:
        rphotos = []
    if len(rphotos) == 10:
        return INSERT_ITEM_IN_WISHLIST
    if not len(photo) == 10:
        rphotos.append(photo)
    redis_helper.save("%s_%s_photos" % (user.id, user.id), str(rphotos))
    caption = message.caption
    if caption:
        caption: str = caption.strip()
        caption: str = caption.split("\n")[0]
        caption: str = re.sub(r"\s{2,}", " ", caption)
    else:
        caption = redis_helper.retrieve("%s_stored_wishlist_element" % user.id)
        caption = caption.decode()
    message_id = redis_helper.retrieve(user.id).decode()
    wishlist_id = get_current_wishlist_id(user.id)
    wishlist_elements = find_wishlist_element_for_user(
        user.id, page_size=4, wishlist_id=wishlist_id
    )
    is_photo = True
    overload = check_message_length(
        message_id,
        chat,
        caption,
        context,
        update,
        user,
        wishlist_elements,
        is_photo,
    )
    return INSERT_ITEM_IN_WISHLIST if is_photo or overload else INSERT_ZELDA


def toggle_cycle_insert(update: Update, context: CallbackContext):
    user: User = update.effective_user
    cycle_insert = redis_helper.retrieve("%s_cycle_insert" % user.id)
    if cycle_insert:
        logger.info("THE CYCLE INSERT IS AVAILABLE")
        if len(cycle_insert) > 0:
            cycle_insert = eval(cycle_insert.decode())
            cycle_insert = not cycle_insert
        else:
            cycle_insert = True
    else:
        cycle_insert = True
    redis_helper.save("%s_cycle_insert" % user.id, str(cycle_insert))
    logger.info("THE CYCLE INSERT VALUE IS [%s]" % cycle_insert)
    add_in_wishlist_element(update, context, cycle_insert, toggle_cycle=True)


def show_step_two_toast(update: Update, context: CallbackContext):
    context.bot.answer_callback_query(
        update.callback_query.id, text=SUPPORTED_LINKS_MESSAGE, show_alert=True
    )
    return INSERT_ZELDA


def go_back(update: Update, context: CallbackContext):
    user: User = update.effective_user
    wishlist_id = get_current_wishlist_id(user.id)
    wish: WishlistElement = find_wishlist_element_for_user(
        update.effective_user.id, 0, 1, wishlist_id=wishlist_id
    )
    if wish:
        wish = wish[0]
        wish.delete()
    if update.callback_query:
        if "from_link" in update.callback_query.data:
            wish.links = []
            wish.save()
            cycle_insert = redis_helper.retrieve("%s_cycle_insert" % user.id)
            if cycle_insert:
                if len(cycle_insert) > 0:
                    cycle_insert = eval(cycle_insert.decode())
                else:
                    cycle_insert = False
            else:
                cycle_insert = False
            add_in_wishlist_element(
                update, context, toggle_cycle=cycle_insert, cycle_insert=cycle_insert
            )
            return INSERT_ITEM_IN_WISHLIST
        elif "from_category" in update.callback_query.data:
            handle_add_confirm(update, context, list(wish.links))
            return INSERT_ZELDA


def create_custom_category(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    wishlist_id = update.callback_query.data.split("_")[-1]
    wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
    title = f"{wishlist.title.upper()}  –  "
    text = WISHLIST_HEADER % title
    text += NEW_CATEGORY_MESSAGE % MAX_CATEGORY_LENGTH
    keyboard = NEW_CUSTOM_CATEGORY_KEYBOARD
    message_id: int = message.message_id
    redis_helper.save("new_category_message_%s" % user.id, str(message_id))
    context.bot.edit_message_text(
        message_id=message_id,
        chat_id=chat.id,
        text=text,
        reply_markup=keyboard,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
    return CREATE_CATEGORY


def new_category_received(update: Update, context: CallbackContext):
    chat: Chat = update.effective_chat
    message: Message = update.effective_message
    user: User = update.effective_user
    message_id = redis_helper.retrieve("new_category_message_%s" % user.id).decode()
    category_name = message.text.lower().capitalize().split("\n")[0]
    emoji_found = emoji.get_emoji_regexp().findall(category_name)
    if emoji_found:
        first_emoji = emoji_found[0]
        if len(emoji_found) > 1:
            emoji_found.pop(0)
        for no_emoji in emoji_found:
            category_name = category_name.replace(no_emoji, "")
        category_name = category_name.replace(first_emoji, "", 1).strip().capitalize()
    else:
        first_emoji = None
    category_name = re.sub(r"\r|\n|\s\s", "", category_name)
    category_name = category_name.strip()
    if len(category_name) > MAX_CATEGORY_LENGTH:
        delete_if_private(message)
        redis_helper.save("new_category_name_%s" % user.id, category_name)
        category_name = max_length_error_format(
            category_name, MAX_CATEGORY_LENGTH, MAX_CATEGORY_LENGTH * 2
        )
        wishlist_id = get_current_wishlist_id(user.id)
        wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
        title = f"{wishlist.title.upper()}  –  "
        if emoji_found:
            emoji_append = CATEGORY_NAME_TOO_LONG_WITH_EMOJI
        else:
            emoji_append = CATEGORY_NAME_TOO_LONG_WITHOUT_EMOJI
        message = (
            f'{WISHLIST_HEADER % title}"{category_name}"\n'
            f"{emoji_append % MAX_CATEGORY_LENGTH}\n{YOU_ARE_CREATING_A_NEW_CATEGORY}\n\n"
            f"{TOO_LONG_NEW_CATEGORY_MESSAGE % MAX_CATEGORY_LENGTH}"
        )
        try:
            context.bot.edit_message_text(
                chat_id=chat.id,
                message_id=message_id,
                text=message,
                disable_web_page_preview=True,
                parse_mode="HTML",
                reply_markup=TOO_LONG_CUSTOM_CATEGORY_KEYBOARD,
            )
        except BadRequest:
            pass
        return CREATE_CATEGORY
    if not emoji_found:
        delete_if_private(message)
        redis_helper.save("new_category_name_%s" % user.id, category_name)
        category_name = max_length_error_format(
            category_name, MAX_CATEGORY_LENGTH, MAX_CATEGORY_LENGTH * 2
        )
        wishlist_id = get_current_wishlist_id(user.id)
        wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
        title = f"{wishlist.title.upper()}  –  "
        message = (
            f'{WISHLIST_HEADER % title}"<code>{category_name}</code>"\n'
            f"{NO_EMOJI_FOUND}\n{YOU_ARE_CREATING_A_NEW_CATEGORY}\n\n"
            f"{TOO_LONG_NEW_CATEGORY_MESSAGE % MAX_CATEGORY_LENGTH}"
        )
        try:
            context.bot.edit_message_text(
                chat_id=chat.id,
                message_id=message_id,
                text=message,
                disable_web_page_preview=True,
                parse_mode="HTML",
                reply_markup=NEW_CUSTOM_CATEGORY_KEYBOARD,
            )
        except BadRequest:
            pass
        return CREATE_CATEGORY
    if not category_name:
        delete_if_private(message)
        redis_helper.save("new_category_name_%s" % user.id, category_name)
        category_name = max_length_error_format(
            category_name, MAX_CATEGORY_LENGTH, MAX_CATEGORY_LENGTH * 2
        )
        wishlist_id = get_current_wishlist_id(user.id)
        wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
        title = f"{wishlist.title.upper()}  –  "
        message = (
            f'{WISHLIST_HEADER % title}"<code>{first_emoji}  ...</code>"\n'
            f"{NO_CATEGORY_NAME_FOUND}\n{YOU_ARE_CREATING_A_NEW_CATEGORY}\n\n"
            f"{TOO_LONG_NEW_CATEGORY_MESSAGE % MAX_CATEGORY_LENGTH}"
        )
        try:
            context.bot.edit_message_text(
                chat_id=chat.id,
                message_id=message_id,
                text=message,
                disable_web_page_preview=True,
                parse_mode="HTML",
                reply_markup=NEW_CUSTOM_CATEGORY_KEYBOARD,
            )
        except BadRequest:
            pass
        return CREATE_CATEGORY
    category_name = "%s  %s" % (first_emoji, category_name)
    create_category_for_user(user.id, category_name)
    handle_insert_for_link(update, context, True)
    return ADD_CATEGORY


def delete_custom_category(update: Update, context: CallbackContext):
    user: User = update.effective_user
    if update.callback_query:
        data = update.callback_query.data
        _id = data.split("_")[-1]
        category: CustomCategory = find_category_for_user_by_id(user.id, _id)
        if category:
            update_category_of_elements(user.id, category.description, CATEGORIES[0])
            category.delete()
        update.callback_query.data = "skip_add_link_to_wishlist_element"
        handle_insert_for_link(update, context)
        return ADD_CATEGORY


def accept_category_modification(update: Update, context: CallbackContext):
    user: User = update.effective_user
    category_name = redis_helper.retrieve("new_category_name_%s" % user.id).decode()
    category_name = category_name[:MAX_CATEGORY_LENGTH]
    create_category_for_user(user.id, category_name)
    handle_insert_for_link(update, context, True)
    return ADD_CATEGORY


ADD_IN_WISHLIST_CONVERSATION = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            add_in_wishlist_element, pattern="add_to_wishlist_element"
        ),
    ],
    states={
        INSERT_ITEM_IN_WISHLIST: [
            MessageHandler(Filters.photo, extract_photo_from_message),
            MessageHandler(Filters.text, handle_add_confirm),
            CallbackQueryHandler(
                callback=handle_add_confirm, pattern="keep_the_current"
            ),
            CallbackQueryHandler(
                callback=toggle_cycle_insert, pattern="toggle_cycle_insert"
            ),
        ],
        INSERT_ZELDA: [
            MessageHandler(Filters.entity("url"), handle_insert_for_link),
            CallbackQueryHandler(
                callback=show_step_two_toast, pattern="show_step_2_advance"
            ),
            CallbackQueryHandler(
                callback=handle_insert_for_link,
                pattern="skip_add_link_to_wishlist_element",
            ),
            CallbackQueryHandler(callback=go_back, pattern="go_back_from_link"),
        ],
        ADD_CATEGORY: [
            CallbackQueryHandler(
                callback=add_category,
                pattern="add_category",
            ),
            CallbackQueryHandler(callback=go_back, pattern="go_back_from_category"),
            CallbackQueryHandler(
                callback=create_custom_category, pattern="create_new_category"
            ),
            CallbackQueryHandler(
                callback=delete_custom_category, pattern="delete_category_custom"
            ),
        ],
        CREATE_CATEGORY: [
            CallbackQueryHandler(
                callback=handle_insert_for_link,
                pattern="skip_add_link_to_wishlist_element",
            ),
            CallbackQueryHandler(
                callback=accept_category_modification,
                pattern="accept_add_link_to_wishlist_element",
            ),
            MessageHandler(Filters.text, new_category_received),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(
            cancel_add_in_wishlist_element, pattern="cancel_add_to_wishlist_element"
        ),
    ],
)
