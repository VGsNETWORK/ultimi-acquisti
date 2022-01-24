#!/usr/bin/env python3

import re
from typing import List

import emoji
import telegram_utils.helper.redis as redis_helper
import telegram_utils.utils.logger as logger
from root.contants.constant import CATEGORIES
from root.contants.keyboard import (
    NEW_CUSTOM_CATEGORY_KEYBOARD,
    TOO_LONG_CUSTOM_CATEGORY_KEYBOARD,
    build_edit_wishlist_element_category_keyboard,
    build_edit_wishlist_element_desc_keyboard,
)
from root.contants.messages import (
    CATEGORY_NAME_TOO_LONG_WITH_EMOJI,
    CATEGORY_NAME_TOO_LONG_WITHOUT_EMOJI,
    EDIT_CATEGORY_TO_WISHLIST_ITEM_MESSAGE,
    EDIT_WISHLIST_PROMPT,
    EDIT_WISHLIST_PROMPT_NO_TARGET_PRICE,
    EDIT_WISHLIST_PROMPT_TARGET_PRICE,
    EDIT_WISHLIST_TARGET_PRICE_PROMPT,
    NEW_CATEGORY_MESSAGE,
    NO_CATEGORY_NAME_FOUND,
    NO_EMOJI_FOUND,
    NOTIFICATION_MODIFIED_CATEGORY,
    NOTIFICATION_MODIFIED_ITEM_LINK_APPEND,
    NOTIFICATION_MODIFIED_ITEM_MESSAGE,
    NOTIFICATION_MODIFIED_ITEM_PHOTOS_APPEND,
    NOTIFICATION_MODIFIED_TITLE,
    TOO_LONG_NEW_CATEGORY_MESSAGE,
    WISHLIST_DESCRIPTION_TOO_LONG,
    WISHLIST_EDIT_STEP_ONE,
    WISHLIST_EDIT_STEP_THREE,
    WISHLIST_HEADER,
    YOU_ARE_CREATING_A_NEW_CATEGORY,
    YOU_ARE_MODIFYING_THIS_ELEMENT,
)
from root.handlers.handlers import extractor
from root.helper.custom_category_helper import (
    create_category_for_user,
    find_categories_for_user,
    find_category_for_user_by_id,
)
from root.helper.notification import create_notification
from root.helper.purchase_helper import convert_to_float
from root.helper.user_helper import get_current_wishlist_id
from root.helper.wishlist import find_wishlist_by_id
from root.helper.wishlist_element import (
    find_wishlist_element_by_id,
    update_category_of_elements,
)
from root.manager.notification_hander import show_notifications
from root.manager.wishlist_element import CREATE_CATEGORY, view_wishlist
from root.manager.wishlist_element_link import view_wishlist_element_links
from root.model.custom_category import CustomCategory
from root.model.user import User
from root.model.wishlist import Wishlist
from root.model.wishlist_element import WishlistElement
from root.util.util import (
    extract_first_link_from_message,
    format_price,
    max_length_error_format,
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
from telegram_utils.utils.tutils import delete_if_private
from bot_util.decorator.maintenance import check_maintenance

EDIT_WISHLIST_TEXT, EDIT_CATEGORY, CREATE_CATEGORY = range(3)

MAX_CATEGORY_LENGTH = 15
MAX_LINK_LENGTH = 27


def show_photo(wishlist_element: WishlistElement):
    return (
        f"  •  <i>{len(wishlist_element.photos)} foto</i>"
        if wishlist_element.photos
        else ""
    )


@check_maintenance
def edit_wishlist_element_item(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    message_id = message.message_id
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    logger.info("RESETTING REMOVE PRICE FLAG TO FALSE")
    redis_helper.save("remove_element_price_%s" % user.id, "false")
    if update.callback_query:
        if "from_link" in update.callback_query.data:
            redis_helper.save("%s_%s_user_link" % (user.id, user.id), "")
    redis_helper.save(user.id, message_id)
    logger.info("THIS IS THE CALLBACK [%s]" % update.callback_query.data)
    _id = update.callback_query.data.split("_")[-1]
    logger.info("EDITING %s" % _id)
    page = int(update.callback_query.data.split("_")[-2])
    wish: WishlistElement = find_wishlist_element_by_id(_id)
    index = update.callback_query.data.split("_")[-3]
    redis_helper.save("%s_%s" % (user.id, user.id), "%s_%s_%s" % (index, page, _id))
    wishlist_id = get_current_wishlist_id(user.id)
    wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
    title = f"{wishlist.title.upper()}  –  "
    message = WISHLIST_HEADER % title
    append = "✏️  <i>Stai modificando questo elemento</i>"
    if not wish:
        update.callback_query.data += "_%s" % page
        view_wishlist(update, context, reset_keyboard=False)
        return
    redis_helper.save("%s_stored_wishlist_element" % user.id, wish.description)
    if wish.user_price:
        price = (
            "  •  🎯  <b><i>%s €</i></b>" % format_price(wish.user_price)
            if wish.user_price
            else None
        )
    else:
        price = ""
    if "rprice" in update.callback_query.data:
        logger.info("SETTING REMOVE PRICE FLAG TO TRUE")
        redis_helper.save("remove_element_price_%s" % user.id, "true")
        price = ""
    message += f"<b>{index}</b>  <code>{wish.description.replace('%', '%%')}</code>     (<i>{wish.category}</i>{show_photo(wish)}{price})\n{append}\n\n"
    # target_price_append = EDIT_WISHLIST_TARGET_PRICE_PROMPT if price else ""
    if not wish.user_price or "rprice" in update.callback_query.data:
        edit_wishlist_message = (
            EDIT_WISHLIST_PROMPT % EDIT_WISHLIST_PROMPT_NO_TARGET_PRICE
        )
    else:
        edit_wishlist_message = EDIT_WISHLIST_PROMPT % EDIT_WISHLIST_PROMPT_TARGET_PRICE
    message += "\n%s%s%s" % (WISHLIST_EDIT_STEP_ONE, edit_wishlist_message, "")
    keyboard = build_edit_wishlist_element_desc_keyboard(
        _id, page, index, show_remove_price=price
    )
    context.bot.edit_message_text(
        chat_id=chat.id,
        text=message,
        message_id=message_id,
        reply_markup=keyboard,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
    return EDIT_WISHLIST_TEXT


@check_maintenance
def edit_wishlist_element_description(
    update: Update, context: CallbackContext, from_new_category: bool = False
):
    logger.info("EDIT_WISHLIST_DESCRIPTION")
    message: Message = update.effective_message
    message_content = update.effective_message.text
    message_id: int = message.message_id
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    if update.callback_query:
        try:
            logger.info("THESE ARE THE INFO [%s]" % update.callback_query.data)
            _id = update.callback_query.data.split("_")[-1]
            page = int(update.callback_query.data.split("_")[-2])
            index = update.callback_query.data.split("_")[-3]
        except Exception:
            info = redis_helper.retrieve(
                "edit_wishlist_element_info_%s" % user.id
            ).decode()
            logger.info("THESE ARE THE INFO [%s]" % info)
            _id = info.split("_")[-1]
            page = int(info.split("_")[-2])
            index = info.split("_")[-3]
        redis_helper.save(
            "edit_wishlist_element_info_%s" % user.id, "%s_%s_%s" % (index, page, _id)
        )
        text = ""
    else:
        context.bot.delete_message(chat_id=chat.id, message_id=message_id)
        message_id = redis_helper.retrieve(user.id).decode()
        data = redis_helper.retrieve("%s_%s" % (user.id, user.id)).decode()
        _id = data.split("_")[-1]
        page = int(data.split("_")[-2])
        index = data.split("_")[-3]
        if not from_new_category:
            text = message_content
            if not update.callback_query:
                redis_helper.save("%s_stored_wishlist_element" % user.id, text)
        else:
            text = redis_helper.retrieve(
                "%s_stored_wishlist_element" % user.id
            ).decode()
    wish: WishlistElement = find_wishlist_element_by_id(_id)
    if not update.callback_query:
        user_price = re.findall(r"%(?:\d{1,})(?:[.,'])?(?:\d{1,})?%", message_content)
        logger.info("THESE IS THE USER PRICE [%s]" % user_price)
        if user_price:
            user_price = user_price[0]
            text = message_content.replace(user_price, "")
            text = text.strip()
            user_price = re.sub("%", "", user_price)
            user_price = user_price.strip()
            user_price = convert_to_float(user_price)
        else:
            user_price = wish.user_price
        if not text:
            text = wish.description
            redis_helper.save("%s_stored_wishlist_element" % user.id, text)
    else:
        user_price = wish.user_price
    if update.callback_query:
        logger.info("THIS IS THE PREVIOUS TITLE [%s]" % "MISSING")
        redis_helper.save(
            "element_description_modified_%s" % update.effective_user.id,
            "0_%s" % "MISSING",
        )
        if "from_category" in update.callback_query.data:
            text = redis_helper.retrieve("%s_stored_wishlist_element" % user.id)
            if text:
                text = text.decode()
            else:
                text = wish.description
    if update.callback_query:
        if "keep_current_description" in update.callback_query.data:
            text = wish.description
            text = redis_helper.save("%s_stored_wishlist_element" % user.id, text)
        if "confirm_description_mod" in update.callback_query.data:
            text = redis_helper.retrieve("%s_stored_wishlist_elemnt" % user.id).decode()
        else:
            text = redis_helper.retrieve(
                "%s_stored_wishlist_element" % user.id
            ).decode()
    if len(text) > 128:
        redis_helper.save("%s_stored_wishlist_element" % user.id, text[:128])
        user_text = max_length_error_format(text, 128, 200)
        wishlist_id = get_current_wishlist_id(user.id)
        wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
        title = f"{wishlist.title.upper()}  –  "
        message = (
            f"{WISHLIST_HEADER % title}<b>1.</b>  {user_text}\n"
            f"{WISHLIST_DESCRIPTION_TOO_LONG}\n{YOU_ARE_MODIFYING_THIS_ELEMENT}\n\n"
        )
        target_price_append = EDIT_WISHLIST_TARGET_PRICE_PROMPT if user_price else ""
        message += "\n%s%s" % (WISHLIST_EDIT_STEP_ONE, EDIT_WISHLIST_PROMPT)
        keyboard = build_edit_wishlist_element_desc_keyboard(_id, page, index, True)
        redis_helper.save("%s_stored_wishlist_element" % user.id, text[:128])
    else:
        ask = "*" if not wish.description == text else ""
        if not wish.description == text:
            logger.info("* THIS IS THE PREVIOUS TITLE [%s]" % wish.description)
            redis_helper.save(
                "element_description_modified_%s" % update.effective_user.id,
                "1_%s" % wish.description,
            )
        else:
            logger.info("THIS IS THE PREVIOUS TITLE [%s]" % wish.description)
            redis_helper.save(
                "element_description_modified_%s" % update.effective_user.id,
                "0_%s" % wish.description,
            )
        redis_helper.save(
            "element_description_modified_%s" % update.effective_user.id,
            "0_%s" % wish.description,
        )
        wish.description = text
        if user_price != "0":
            wish.user_price = user_price
        logger.info("IMMABOUTOSAVETHIS [%s]" % user_price)
        if not user_price:
            user_price = 0
        redis_helper.save(
            "element_price_modified_%s" % update.effective_user.id, user_price
        )
        redis_helper.save("%s_stored_wishlist_element" % user.id, text)
        wishlist_id = get_current_wishlist_id(user.id)
        wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
        title = f"{wishlist.title.upper()}  –  "
        message = WISHLIST_HEADER % title
        append = "✏️  <i>Stai modificando questo elemento</i>"
        if user_price:
            price = "  •  🎯  <b><i>%s €</i></b>" % format_price(user_price)
        else:
            price = ""
        remove_price = redis_helper.retrieve(
            "remove_element_price_%s" % user.id
        ).decode()

        if remove_price.lower() == "true":
            logger.info("REMOVE PRICE FLAG IS TRUE =[%s]" % remove_price)
            price = ""
        message += f"<b>{index}</b>  {ask}<b>{wish.description}</b>     (<b><i>{wish.category}</i></b>{show_photo(wish)}{price})\n{append}\n\n"

        append = EDIT_CATEGORY_TO_WISHLIST_ITEM_MESSAGE
        message += f"\n{WISHLIST_EDIT_STEP_THREE}{append}"
        message += EDIT_WISHLIST_TARGET_PRICE_PROMPT if price else ""
        categories: List[CustomCategory] = find_categories_for_user(
            user_id=update.effective_user.id
        )
        keyboard = build_edit_wishlist_element_category_keyboard(
            _id, page, index, wish.category, categories
        )

    context.bot.edit_message_text(
        chat_id=chat.id,
        text=message,
        message_id=message_id,
        reply_markup=keyboard,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
    return EDIT_CATEGORY if len(text) <= 128 else EDIT_WISHLIST_TEXT


@check_maintenance
def edit_wishlist_element_link(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    message_id: int = message.message_id
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    if update.callback_query:
        _id = update.callback_query.data.split("_")[-1]
        page = int(update.callback_query.data.split("_")[-2])
        index = update.callback_query.data.split("_")[-3]
        link = None
    else:
        context.bot.delete_message(chat_id=chat.id, message_id=message_id)
        message_id = redis_helper.retrieve(user.id).decode()
        data = redis_helper.retrieve("%s_%s" % (user.id, user.id)).decode()
        _id = data.split("_")[-1]
        page = int(data.split("_")[-2])
        index = data.split("_")[-3]
        link = message.text if message.text else message.caption
        link = extract_first_link_from_message(update.effective_message)
        redis_helper.save("%s_%s_user_link" % (user.id, user.id), link)
        logger.info(link)
    wish: WishlistElement = find_wishlist_element_by_id(_id)
    if update.callback_query:
        if not "remove_link" in update.callback_query.data:
            if link:
                pictures = extractor.load_url(link)
                pictures = pictures[:10]
            else:
                pictures = []
        else:
            pictures = []
    else:
        pictures = extractor.load_url(link)
        pictures = pictures[:10]
    redis_helper.save("%s_%s_photos" % (user.id, user.id), str(pictures))
    logger.info("THESE ARE THE PICTURES %s" % pictures)
    if update.callback_query:
        if "remove_link" in update.callback_query.data:
            removed = "1"
            redis_helper.save("%s_removed_link" % user.id, removed)
        else:
            removed = "0"
            redis_helper.save("%s_removed_link" % user.id, removed)
    else:
        removed = "0"
        redis_helper.save("%s_removed_link" % user.id, removed)
        wish.links = link
    text = redis_helper.retrieve("%s_stored_wishlist_element" % user.id).decode()
    ask = "*" if not wish.description == text else ""
    ask = "*" if removed == "1" else ask
    ask = "*" if not update.callback_query else ask
    logger.info("THIS IS THE ASK")
    if ask:
        redis_helper.save(
            "element_description_modified_%s" % update.effective_user.id,
            "1_%s" % wish.description,
        )
    else:
        redis_helper.save(
            "element_description_modified_%s" % update.effective_user.id,
            "0_%s" % wish.description,
        )
    wish.description = text
    redis_helper.save("%s_stored_wishlist_element" % user.id, text)
    wishlist_id = get_current_wishlist_id(user.id)
    wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
    title = f"{wishlist.title.upper()}  –  "
    message = WISHLIST_HEADER % title
    append = "✏️  <i>Stai modificando questo elemento</i>"
    message += f"<b>{index}</b>  {ask}<b>{wish.description}</b>     (<b><i>{wish.category}</i></b>{show_photo(wish)})\n{append}\n\n"
    message += "\n%s%s" % (
        WISHLIST_EDIT_STEP_THREE,
        EDIT_CATEGORY_TO_WISHLIST_ITEM_MESSAGE,
    )
    categories: List[CustomCategory] = find_categories_for_user(
        user_id=update.effective_user.id
    )
    context.bot.edit_message_text(
        message_id=message_id,
        chat_id=chat.id,
        text=message,
        reply_markup=build_edit_wishlist_element_category_keyboard(
            _id, page, index, wish.category, categories
        ),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
    return EDIT_CATEGORY


@check_maintenance
def edit_category(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    user: User = update.effective_user
    context.bot.answer_callback_query(update.callback_query.id)
    data = update.callback_query.data
    _id = data.split("_")[-1]
    if "keep_category" in data:
        cancel_edit_wishlist_element(update, context)
        return ConversationHandler.END
    if not "custom" in data:
        category = int(data.split("_")[-4])
    else:
        info = redis_helper.retrieve("%s_%s" % (user.id, user.id)).decode()
        update.callback_query.data += "_%s" % info
        category: CustomCategory = find_category_for_user_by_id(
            user.id, data.split("_")[-1]
        )
        category = category.description
        logger.info("THESE ARE THE INFO %s" % info)
        _id = info.split("_")[-1]
    logger.info("SEARCHING ELEMENT WITH ID %s" % _id)
    wish: WishlistElement = find_wishlist_element_by_id(_id)
    text = redis_helper.retrieve("%s_stored_wishlist_element" % user.id).decode()
    previous_description = wish.description
    wish.description = text
    previous_category = wish.category
    if not "custom" in data:
        wish.category = CATEGORIES[category]
    else:
        wish.category = category
    rphotos: List[str] = redis_helper.retrieve("%s_%s_photos" % (user.id, user.id))
    rphotos = eval(rphotos.decode()) if rphotos else None
    wish.photos = rphotos if rphotos else wish.photos
    user_price: float = float(
        redis_helper.retrieve(
            "element_price_modified_%s" % update.effective_user.id
        ).decode()
    )
    remove_price = redis_helper.retrieve("remove_element_price_%s" % user.id).decode()
    if remove_price.lower() == "true":
        price = ""
        wish.user_price = None
    else:
        if user_price != 0:
            if user_price != wish.user_price:
                wish.user_price = user_price
    wish.save()
    wishlist: Wishlist = find_wishlist_by_id(wish.wishlist_id)
    description_modified: str = text
    element_extra = []
    modification_list = []
    show_notification = False
    previous_name = wish.description
    if wish.photos:
        element_extra.append(
            NOTIFICATION_MODIFIED_ITEM_PHOTOS_APPEND % len(wish.photos)
        )
    if wish.links:
        element_extra.append(NOTIFICATION_MODIFIED_ITEM_LINK_APPEND % len(wish.links))
        for link in wish.links:
            if len(link) >= MAX_LINK_LENGTH:
                link = '        •  <a href="%s">%s...</a>' % (
                    link,
                    link[: MAX_LINK_LENGTH - 3],
                )
            else:
                link = '        •  <a href="%s">%s</a>' % (link, link)
            element_extra.append(link)
    logger.info(f"THIS IS THE DESCRIPTION: [{description_modified}]")
    if description_modified != previous_description:
        previous_name = description_modified.replace("1_", "", 1)
        show_notification = True
        logger.info("THIS IS THE PREVIOUS TITLE [%s]" % previous_name)
        modification_list.append(NOTIFICATION_MODIFIED_TITLE % wish.description)
    if previous_category != wish.category:
        show_notification = True
        modification_list.append(NOTIFICATION_MODIFIED_CATEGORY % wish.category)
    format_text = [previous_name]
    if modification_list:
        modification_list = "\n%s" % "\n".join(modification_list)
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
        element_extra = " "
    format_text.append(previous_category)
    format_text.append(element_extra)
    format_text.append(wishlist.title)
    format_text.append(modification_list)
    notification_message = NOTIFICATION_MODIFIED_ITEM_MESSAGE % tuple(format_text)
    if show_notifications:
        create_notification(update.effective_user.id, notification_message)
    cancel_edit_wishlist_element(update, context)
    return ConversationHandler.END


@check_maintenance
def cancel_edit_wishlist_element(update: Update, context: CallbackContext):
    if update.callback_query:
        page = update.callback_query.data.split("_")[-2]
        update.callback_query.data += "_%s" % page
        view_wishlist(update, context, reset_keyboard=False)
    else:
        view_wishlist(update, context, None, "0", reset_keyboard=False)
    return ConversationHandler.END


@check_maintenance
def go_back(update: Update, context: CallbackContext):
    if update.callback_query:
        if "from_category" in update.callback_query.data:
            edit_wishlist_element_item(update, context)
            return EDIT_WISHLIST_TEXT


def create_custom_category(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    wishlist_id = update.callback_query.data.split("_")[-1]
    wishlist_id: str = get_current_wishlist_id(user.id)
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


@check_maintenance
def accept_category_modification(update: Update, context: CallbackContext):
    user: User = update.effective_user
    category_name = redis_helper.retrieve("new_category_name_%s" % user.id).decode()
    category_name = category_name[:MAX_CATEGORY_LENGTH]
    create_category_for_user(user.id, category_name)
    edit_wishlist_element_description(update, context)
    return EDIT_CATEGORY


@check_maintenance
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
    category_name = re.sub(r"\\x[a-fA-F0-9]{2}|b'|'$", "", str(category_name.encode()))
    logger.info(
        "THIS IS THE NAME [%s] [%s]" % (category_name.encode(), len(category_name))
    )
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
    edit_wishlist_element_description(update, context, True)
    return EDIT_CATEGORY


@check_maintenance
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
        edit_wishlist_element_description(update, context)
        return EDIT_CATEGORY


@check_maintenance
def go_to_link_session(update: Update, context: CallbackContext):
    view_wishlist_element_links(update, context)
    return ConversationHandler.END


@check_maintenance
def remove_element_price(update: Update, context: CallbackContext):
    logger.info("***REMOVING PRICE***")
    update.callback_query.data = update.callback_query.data.replace(
        "remove_element_price", "edit_wishlist_element_item_rprice"
    )
    edit_wishlist_element_item(update, context)
    return EDIT_WISHLIST_TEXT


EDIT_WISHLIST_CONVERSATION = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            edit_wishlist_element_item,
            pattern="edit_wishlist_element_item",
        ),
    ],
    states={
        EDIT_WISHLIST_TEXT: [
            MessageHandler(
                Filters.text,
                edit_wishlist_element_description,
            ),
            CallbackQueryHandler(
                callback=remove_element_price,
                pattern="remove_element_price",
            ),
            CallbackQueryHandler(
                callback=edit_wishlist_element_description,
                pattern="keep_current_description",
            ),
            CallbackQueryHandler(
                callback=edit_wishlist_element_description,
                pattern="confirm_description_mod",
            ),
            CallbackQueryHandler(
                callback=go_to_link_session, pattern="go_to_link_session"
            ),
        ],
        EDIT_CATEGORY: [
            CallbackQueryHandler(
                callback=edit_category,
                pattern="edit_category",
            ),
            CallbackQueryHandler(
                callback=create_custom_category, pattern="create_new_category"
            ),
            CallbackQueryHandler(
                callback=delete_custom_category, pattern="delete_category_custom"
            ),
            CallbackQueryHandler(callback=go_back, pattern="go_back_from_category"),
        ],
        CREATE_CATEGORY: [
            CallbackQueryHandler(
                callback=edit_wishlist_element_description,
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
            callback=edit_wishlist_element_link, pattern="keep_category"
        ),
        CallbackQueryHandler(
            cancel_edit_wishlist_element,
            pattern="cancel_add_to_wishlist_element",
        ),
    ],
)
