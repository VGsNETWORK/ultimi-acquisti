#!/usr/bin/env python3
# region
import operator
import re

from telegram import message
from root.helper import wishlist_element
from root.model.wishlist import Wishlist
from root.manager.view_other_wishlists import view_other_wishlists
from root.helper.user_helper import (
    create_user,
    get_current_wishlist_id,
    retrieve_user,
    user_exists,
)
from root.helper.wishlist import (
    count_all_wishlists_for_user,
    create_wishlist_if_empty,
    find_wishlist_by_id,
)
from typing import List
from telegram.files.inputmedia import InputMediaPhoto

from telegram.files.photosize import PhotoSize
from telegram_utils.utils.tutils import delete_if_private
from root.contants.constant import CATEGORIES
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from root.contants.messages import (
    ADDED_TO_WISHLIST,
    ADD_CATEGORY_TO_WISHLIST_ITEM_MESSAGE,
    ADD_LINK_TO_WISHLIST_ITEM_MESSAGE,
    ADD_TO_WISHLIST_MAX_PHOTOS_PROMPT,
    ADD_TO_WISHLIST_PROMPT,
    ADD_TO_WISHLIST_START_PROMPT,
    CYCLE_INSERT_ENABLED_APPEND,
    DELETE_ALL_WISHLIST_ITEMS_AND_LIST_MESSAGE,
    DELETE_WISHLIST_ITEMS_AND_PHOTOS_APPEND,
    DELETE_ALL_WISHLIST_ITEMS_MESSAGE,
    DELETE_ALL_WISHLIST_ITEMS_NO_PHOTO_MESSAGE,
    DELETE_WISHLIST_ITEMS_APPEND,
    EDIT_WISHLIST_LINK_NO_PHOTOS,
    NO_ELEMENT_IN_WISHLIST,
    SUPPORTED_LINKS_MESSAGE,
    WISHLIST_DESCRIPTION_TOO_LONG,
    WISHLIST_HEADER,
    WISHLIST_LEGEND_APPEND_FIRST_PAGE,
    WISHLIST_LEGEND_APPEND_LEGEND,
    WISHLIST_LEGEND_APPEND_SECOND_PAGE,
    WISHLIST_LEGEND_APPEND_SECOND_PAGE_ONLY,
    WISHLIST_STEP_ONE,
    WISHLIST_STEP_THREE,
    WISHLIST_STEP_TWO,
)
from root.util.util import (
    create_button,
    extract_first_link_from_message,
    max_length_error_format,
)
from root.helper.wishlist_element import (
    count_all_wishlist_elements_for_user,
    count_all_wishlist_elements_for_wishlist_id,
    count_all_wishlist_elements_photos,
    delete_all_wishlist_element_for_user,
    find_wishlist_element_by_id,
    find_wishlist_element_for_user,
    get_total_wishlist_element_pages_for_user,
    remove_wishlist_element_item_for_user,
)
from root.model.wishlist_element import WishlistElement
from root.contants.keyboard import (
    ADD_LINK_TO_WISHLIST_ITEM,
    ADD_LINK_TO_WISHLIST_ITEM_NO_LINK,
    ADD_TO_WISHLIST_ABORT_CYCLE_KEYBOARD,
    ADD_TO_WISHLIST_ABORT_NO_CYCLE_KEYBOARD,
    ADD_TO_WISHLIST_ABORT_TOO_LONG_KEYBOARD,
    build_add_wishlist_element_category_keyboard,
    create_delete_all_wishlist_element_items_keyboard,
    create_wishlist_element_keyboard,
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
from difflib import SequenceMatcher

# endregion

INSERT_ITEM_IN_WISHLIST, INSERT_ZELDA, ADD_CATEGORY = range(3)

MAX_LINK_LENGTH = 27


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
):
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
            f"{WISHLIST_DESCRIPTION_TOO_LONG}"
        )
        if wishlist_elements:
            logger.info("ELEMENTS FOUND, CREATING MESSAGE...")
            message += "\n".join(
                [
                    (
                        f"<b>{index + 2}.</b>  {wish.description}\n"
                        f"<i>{wish.category}</i>{has_photo(wish)}{has_link(wish)}  •  <i>Aggiunto il {wish.creation_date.strftime('%d/%m/%Y')}</i>\n"
                    )
                    for index, wish in enumerate(wishlist_elements)
                ]
            )
            append = (
                ADD_TO_WISHLIST_PROMPT % (10 - len(rphotos))
                if len(rphotos) < 10
                else ADD_TO_WISHLIST_MAX_PHOTOS_PROMPT
            )
            message += "\n\n%s%s" % (WISHLIST_STEP_ONE, append)
        else:
            logger.info("NO ELEMENTS FOUND, CREATING MESSAGE...")
            append = (
                ADD_TO_WISHLIST_PROMPT % (10 - len(rphotos))
                if len(rphotos) < 10
                else ADD_TO_WISHLIST_MAX_PHOTOS_PROMPT
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
            wishlist_elements = wishlist_elements[:4]
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
                            f"<i>{wish.category}</i>{has_photo(wish)}{has_link(wish)}  •  <i>Aggiunto il {wish.creation_date.strftime('%d/%m/%Y')}</i>\n"
                        )
                        for index, wish in enumerate(wishlist_elements)
                    ]
                )
            if wishlist_elements:
                if len(wishlist_elements) > 1:
                    message += "\n"
            cycle_message = CYCLE_INSERT_ENABLED_APPEND if cycle_enabled(user) else ""
            append = ADD_LINK_TO_WISHLIST_ITEM_MESSAGE % EDIT_WISHLIST_LINK_NO_PHOTOS
            message += f"\n\n{WISHLIST_STEP_TWO}{append}{cycle_message}"
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
                            f"<i>{wish.category}</i>{has_photo(wish)}{has_link(wish)}  •  <i>Aggiunto il {wish.creation_date.strftime('%d/%m/%Y')}</i>\n"
                        )
                        for index, wish in enumerate(wishlist_elements)
                    ]
                )
                append = (
                    ADD_TO_WISHLIST_PROMPT % (10 - len(rphotos))
                    if len(rphotos) < 10
                    else ADD_TO_WISHLIST_MAX_PHOTOS_PROMPT
                )
                message += "\n\n%s%s" % (WISHLIST_STEP_ONE, append)
            else:
                logger.info("NO ELEMENTS FOUND...")
                append = (
                    ADD_TO_WISHLIST_PROMPT % (10 - len(rphotos))
                    if len(rphotos) < 10
                    else ADD_TO_WISHLIST_MAX_PHOTOS_PROMPT
                )
                message += "\n%s%s" % (WISHLIST_STEP_ONE, append)
            context.bot.edit_message_text(
                chat_id=chat.id,
                message_id=message_id,
                text=message,
                reply_markup=ADD_TO_WISHLIST_ABORT_NO_CYCLE_KEYBOARD,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
        return False


def has_photo(wishlist_element: WishlistElement):
    if wishlist_element.user_id == 84872221:
        return ""
    return "  •  🖼" if wishlist_element.photos else ""


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
    wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
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
        remove_wishlist_element_item_for_user(_id)
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
            context.bot.delete_message(chat_id=chat.id, message_id=message_id)
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
    message: Message = update.effective_message
    message_id = message.message_id
    chat: Chat = update.effective_chat
    user: User = update.effective_user
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
            msgs.append(
                f"<b>{space}{index}.</b>  {wish.description}\n"
                f"<i>{wish.category}</i>{has_photo(wish)}{has_link(wish)}  •  <i>Aggiunto il {wish.creation_date.strftime('%d/%m/%Y')}</i>{new_line}"
            )
        message += "\n".join(msgs)
        if append and under_first:
            wishlist_elements.insert(0, wish)
    else:
        inc = 0
        message = NO_ELEMENT_IN_WISHLIST
    wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
    title = f"{wishlist.title.upper()}  –  "
    message = "%s%s" % (WISHLIST_HEADER % title, message)
    first_page = page + 1 == 1
    last_page = page + 1 == total_pages
    total_wishlists = count_all_wishlists_for_user(user.id)
    if total_pages > 1:
        message += (
            f"\n\n<i>Questa lista dei desideri contiene <b>%s</b> elementi.</i>"
            % count_all_wishlist_elements_for_wishlist_id(wishlist_id, user.id)
        )
    if len(list(wishlist_elements)) > 0:
        message += WISHLIST_LEGEND_APPEND_LEGEND
    if not under_first and append:
        if len(wishlist_elements) > 0:
            message += f"\n\n{append}"
        else:
            message += f"\n\n\n{append}"
    if not reset_keyboard:
        first_page_added = False
        second_page_added = False
        append_legend = []
        extra_spaces = ""
        for index in range(1, len(wishlist_elements) + 1):
            element = redis_helper.retrieve(
                "%s_second_element_page_%s." % (user.id, index + (5 * page))
            ).decode()
            if element:
                element = eval(element)
                if element:
                    if not second_page_added:
                        if len(list(wishlist_elements)) > 0:
                            append_legend.append(WISHLIST_LEGEND_APPEND_SECOND_PAGE)
                            second_page_added = True
                    extra_spaces += "&#8203;"
                else:
                    if not first_page_added:
                        if len(list(wishlist_elements)) > 0:
                            append_legend.insert(0, WISHLIST_LEGEND_APPEND_FIRST_PAGE)
                            first_page_added = True
        if len(append_legend) == 1:
            if append_legend[0] == WISHLIST_LEGEND_APPEND_SECOND_PAGE:
                message += WISHLIST_LEGEND_APPEND_SECOND_PAGE_ONLY
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
    if update.callback_query:
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
    redis_helper.save("%s_%s_photos" % (user.id, user.id), "")
    if not toggle_cycle:
        redis_helper.save("%s_cycle_insert" % user.id, str(False))


def add_in_wishlist_element(
    update: Update,
    context: CallbackContext,
    cycle_insert: bool = False,
    toggle_cycle: bool = False,
):
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
    message = (
        f"{WISHLIST_HEADER % title}<b>1.</b>  . . . . . .\n"
        "✍🏻  <i>Stai inserendo questo elemento</i>\n\n"
    )
    if wishlist_elements:
        message += "\n".join(
            [
                (
                    f"<b>{index + 2}.</b>  {wish.description}\n"
                    f"<i>{wish.category}</i>{has_photo(wish)}{has_link(wish)}  •  <i>Aggiunto il {wish.creation_date.strftime('%d/%m/%Y')}</i>\n"
                )
                for index, wish in enumerate(wishlist_elements)
            ]
        )
        append = (
            ADD_TO_WISHLIST_START_PROMPT
            if len(rphotos) < 10
            else ADD_TO_WISHLIST_MAX_PHOTOS_PROMPT
        )
        message += "\n\n%s%s" % (WISHLIST_STEP_ONE, append)
    else:
        append = (
            ADD_TO_WISHLIST_START_PROMPT
            if len(rphotos) < 10
            else ADD_TO_WISHLIST_MAX_PHOTOS_PROMPT
        )
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
        category = int(data.split("_")[-1])
        wish.photos = rphotos
        wish.category = CATEGORIES[category]
        user = retrieve_user(user.id)
        if user:
            wish.wishlist_id = user.current_wishlist
        wish.save()
        cycle_insert = redis_helper.retrieve("%s_cycle_insert" % user.user_id)
        logger.info("THE CYCLE INSERT VALUE IS [%s]" % cycle_insert)
        if cycle_insert:
            logger.info("THE CYCLE INSERT IS AVAILABLE")
            if len(cycle_insert) > 0:
                cycle_insert = eval(cycle_insert.decode())
                if cycle_insert:
                    add_in_wishlist_element(update, context, cycle_insert, cycle_insert)
                    return INSERT_ITEM_IN_WISHLIST
        view_wishlist(update, context, ADDED_TO_WISHLIST, "0", reset_keyboard=True)
        return ConversationHandler.END


def cancel_add_in_wishlist_element(update: Update, context: CallbackContext):
    data = update.callback_query.data
    if not "NO_DELETE" in data:
        user: User = update.effective_user
        wishlist_id = get_current_wishlist_id(user.id)
        wish: WishlistElement = find_wishlist_element_for_user(
            user.id, 0, 1, wishlist_id=wishlist_id
        )
        if wish:
            wish = wish[0]
            wish.delete()
    update.callback_query.data += "_0"
    view_wishlist(update, context, reset_keyboard=False)
    return ConversationHandler.END


def handle_insert_for_link(update: Update, context: CallbackContext):
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
            wishlist_link = extract_first_link_from_message(update.effective_message)
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
                    "%s_%s_duplicated_links" % (user.id, user.id), str(duplicated_links)
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
        message += "\n".join(
            [
                (
                    f"<b>{index + 2}.</b>  {wish.description}\n"
                    f"<i>{wish.category}</i>{has_photo(wish)}{has_link(wish)}  •  <i>Aggiunto il {wish.creation_date.strftime('%d/%m/%Y')}</i>\n"
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
    if not update.callback_query:
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
            )
            return INSERT_ZELDA
    context.bot.edit_message_text(
        message_id=message_id,
        chat_id=chat.id,
        text=message,
        reply_markup=build_add_wishlist_element_category_keyboard(),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
    return ADD_CATEGORY


def reset_redis_wishlist_keyboard(user_id: int, total_elements: int):
    for index in range(0, total_elements + 1):
        redis_helper.save("%s_second_element_page_%s." % (user_id, index), "False")


def toggle_element_action_page(update: Update, context: CallbackContext):
    user: User = update.effective_user
    index = update.callback_query.data.split("_")[-3]
    second_page = redis_helper.retrieve("%s_second_element_page_%s" % (user.id, index))
    if second_page:
        second_page: second_page.decode()
        if second_page:
            second_page: bool = eval(second_page)
        else:
            second_page: False
    else:
        second_page = False
    second_page = not second_page
    redis_helper.save("%s_second_element_page_%s" % (user.id, index), str(second_page))

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
        ],
    },
    fallbacks=[
        CallbackQueryHandler(
            cancel_add_in_wishlist_element, pattern="cancel_add_to_wishlist_element"
        ),
    ],
)
