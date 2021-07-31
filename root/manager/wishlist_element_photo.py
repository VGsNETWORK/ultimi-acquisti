#!/usr/bin/env python3

from root.helper.user_helper import get_current_wishlist_id
from root.helper.wishlist import find_wishlist_by_id, find_wishlist_for_user
from root.handlers.handlers import extractor
from root.contants.messages import (
    ASK_FOR_PHOTOS_PREPEND,
    DELETE_ALL_WISHLIST_ITEMS_PHOTOS,
    MALFORMED_VALID_LINK_APPEND,
    NOT_SUPPORTED_LINK_APPEND,
    REQUEST_WISHLIST_PHOTO,
    SINGLE_WISHLIST_PHOTO_ADDED,
    VIEW_WISHLIST_PHOTO_MESSAGE,
    VIEW_NO_WISHLIST_PHOTO_MESSAGE,
    WISHLIST_HEADER,
    WISHLIST_PHOTO_LIMIT_REACHED,
)
from telegram.error import BadRequest
from root.manager.wishlist_element import view_wishlist
from root.contants.keyboard import (
    build_view_wishlist_element_photos_keyboard,
    create_cancel_wishlist_element_photo_keyboard,
    create_delete_all_wishlist_element_photos_keyboard,
)
from telegram.chat import Chat
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.ext.conversationhandler import ConversationHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram.files.inputmedia import InputMediaPhoto
from root.model.wishlist_element import WishlistElement
from root.helper.wishlist_element import (
    add_photo,
    delete_wishlist_element_photos,
    find_wishlist_element_by_id,
    remove_photo,
)
from typing import List
from telegram import Update
from telegram.ext import CallbackContext
from telegram.files.photosize import PhotoSize
from telegram.message import Message
from telegram.user import User
import telegram_utils.utils.logger as logger
import operator
import telegram_utils.helper.redis as redis_helper
from telegram_utils.utils.tutils import delete_if_private


ADD_PHOTO = range(1)


def ask_delete_all_wishlist_element_photos(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    wish_id = redis_helper.retrieve("%s_%s" % (user.id, user.id)).decode()
    wishlist_element: WishlistElement = find_wishlist_element_by_id(wish_id)
    context.bot.edit_message_text(
        chat_id=chat.id,
        message_id=message.message_id,
        text=DELETE_ALL_WISHLIST_ITEMS_PHOTOS
        % (len(wishlist_element.photos), wishlist_element.description),
        reply_markup=create_delete_all_wishlist_element_photos_keyboard(),
        disable_web_page_preview=True,
        parse_mode="HTML",
    )


def confirm_delete_all_wishlist_element_photos(
    update: Update, context: CallbackContext
):
    user: User = update.effective_user
    message: Message = update.effective_message
    wish_id = redis_helper.retrieve("%s_%s" % (user.id, user.id)).decode()
    messages = redis_helper.retrieve("%s_photos_message" % update.effective_user.id)
    if messages:
        messages = messages.decode()
        messages: List[str] = eval(messages)
    else:
        messages = []
    messages = [str(m) for m in messages]
    logger.info(messages)
    try:
        for message_id in messages:
            context.bot.delete_message(chat_id=message.chat_id, message_id=message_id)
    except BadRequest:
        pass
    delete_wishlist_element_photos(wish_id)
    update.callback_query.data += "_%s" % wish_id
    page = redis_helper.retrieve("%s_current_page" % user.id).decode()
    update.callback_query.data += "_%s" % page
    view_wishlist(update, context, reset_keyboard=False)


def abort_delete_all_wishlist_element_photos(update: Update, context: CallbackContext):
    user: User = update.effective_user
    chat: Chat = update.effective_chat
    message: Message = update.effective_message
    message_id = message.message_id
    messages = redis_helper.retrieve("%s_photos_message" % update.effective_user.id)
    if messages:
        messages = messages.decode()
        messages: List[str] = eval(messages)
    else:
        messages = []
    messages = [str(m) for m in messages]
    wish_id = redis_helper.retrieve("%s_%s" % (user.id, user.id)).decode()
    update.callback_query.data += "_%s" % wish_id
    # view_wishlist_element_photos(update, context)
    wishlist_element: WishlistElement = find_wishlist_element_by_id(wish_id)
    photos: List[str] = wishlist_element.photos
    if not photos:
        text: str = VIEW_NO_WISHLIST_PHOTO_MESSAGE % (wishlist_element.description)
        wishlist_id = get_current_wishlist_id(user.id)
        wishlist = find_wishlist_by_id(wishlist_id)
        title = f"{wishlist.title.upper()}  –  "
        text = f"{WISHLIST_HEADER % title}{text}"
        keyboard = build_view_wishlist_element_photos_keyboard(wishlist_element, [])
    else:
        text = VIEW_WISHLIST_PHOTO_MESSAGE % (
            len(wishlist_element.photos),
            wishlist_element.description,
        )
        logger.info("sending %s photos" % len(photos))
        message = [m for m in messages]
        keyboard = build_view_wishlist_element_photos_keyboard(
            wishlist_element, message
        )
    context.bot.edit_message_text(
        chat_id=chat.id,
        message_id=message_id,
        text=text,
        reply_markup=keyboard,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


def delete_wishlist_element_photo(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    message_id = update.callback_query.data.split("_")[-1]
    logger.info(
        "GETTING MESSAGE_ID FROM CALLBACKQUERY [%s]" % update.callback_query.data
    )
    logger.info("DELETING MESSAGE WITH MESSAGE_ID [%s]" % message_id)
    context.bot.delete_message(chat_id=message.chat_id, message_id=message_id)
    wish_id = redis_helper.retrieve("%s_%s" % (user.id, user.id)).decode()
    wishlist_element: WishlistElement = find_wishlist_element_by_id(wish_id)
    photos: List[str] = wishlist_element.photos
    messages = redis_helper.retrieve("%s_photos_message" % user.id)
    if messages:
        messages = messages.decode()
        messages: List[str] = eval(messages)
    else:
        messages = []
    messages = [str(m) for m in messages]
    index = messages.index(str(message_id))
    photo = photos[index]
    photos.remove(photo)
    wishlist_element.photos = photos
    remove_photo(wish_id, photo)
    messages.remove(str(message_id))
    redis_helper.save("%s_photos_message" % user.id, str(messages))
    if not photos:
        text: str = VIEW_NO_WISHLIST_PHOTO_MESSAGE % (wishlist_element.description)
        wishlist_id = get_current_wishlist_id(user.id)
        wishlist = find_wishlist_by_id(wishlist_id)
        title = f"{wishlist.title.upper()}  –  "
        text = f"{WISHLIST_HEADER % title}{text}"
        keyboard = build_view_wishlist_element_photos_keyboard(wishlist_element, [])
    else:
        text = VIEW_WISHLIST_PHOTO_MESSAGE % (
            len(wishlist_element.photos),
            wishlist_element.description,
        )
        keyboard = build_view_wishlist_element_photos_keyboard(
            wishlist_element, messages
        )
    context.bot.edit_message_text(
        chat_id=chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=keyboard,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


def delete_photos_and_go_to_wishlist_element(update: Update, context: CallbackContext):
    user: User = update.effective_user
    message: Message = update.effective_message
    messages = redis_helper.retrieve("%s_photos_message" % user.id)
    if messages:
        messages = messages.decode()
        messages = eval(messages)
        logger.info(messages)
        try:
            for message_id in messages:
                context.bot.delete_message(
                    chat_id=message.chat_id, message_id=message_id
                )
        except BadRequest as e:
            logger.error(e)
    data = update.callback_query.data
    page = redis_helper.retrieve("%s_current_page" % user.id).decode()
    redis_helper.save(user.id, message.message_id)
    logger.info("THIS NEEDS TO BE EDITED %s " % message.message_id)
    if not page:
        page: str = data.split("_")[-1]
    logger.info("%s this is the page" % page)
    view_wishlist(update, context, page=int(page), reset_keyboard=False)


def view_wishlist_element_photos(
    update: Update,
    context: CallbackContext,
    append: str = None,
    send_photo: bool = True,
):
    message: Message = update.effective_message
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    message_id = redis_helper.retrieve("%s_ask_photo_message" % user.id).decode()
    message_id = message_id if append else message.message_id
    if update.callback_query:
        data: str = update.callback_query.data
        logger.info("CALLBACK %s" % data)
        wish_id: str = data.split("_")[-1]
        page: str = data.split("_")[-2]
        if not page.isnumeric():
            page = redis_helper.retrieve("%s_current_page" % user.id).decode()
        redis_helper.save("%s_current_page" % user.id, page)
    else:
        wish_id = redis_helper.retrieve("%s_%s" % (user.id, user.id)).decode()
    redis_helper.save("%s_%s" % (user.id, user.id), wish_id)
    wishlist_element: WishlistElement = find_wishlist_element_by_id(wish_id)
    if not wishlist_element:
        update.callback_query.data += "_%s" % page
        view_wishlist(update, context, reset_keyboard=False)
        return
    photos: List[str] = wishlist_element.photos
    if not photos:
        text: str = VIEW_NO_WISHLIST_PHOTO_MESSAGE % (wishlist_element.description)
        wishlist_id = get_current_wishlist_id(user.id)
        wishlist = find_wishlist_by_id(wishlist_id)
        title = f"{wishlist.title.upper()}  –  "
        text = f"{WISHLIST_HEADER % title}{text}"
        keyboard = build_view_wishlist_element_photos_keyboard(wishlist_element, [])
    else:
        logger.info(message_id)
        if send_photo:
            logger.info("deleting message")
            context.bot.delete_message(chat_id=message.chat_id, message_id=message_id)
        text = VIEW_WISHLIST_PHOTO_MESSAGE % (
            len(wishlist_element.photos),
            wishlist_element.description,
        )
        logger.info("sending %s photos" % len(photos))
        photos = [InputMediaPhoto(media=photo) for photo in photos]
        if len(photos) > 1:
            if send_photo:
                message: List[Message] = context.bot.send_media_group(
                    chat_id=chat.id, media=photos
                )
                message = [m.message_id for m in message]
                redis_helper.save("%s_photos_message" % user.id, str(message))
            keyboard = build_view_wishlist_element_photos_keyboard(
                wishlist_element, message
            )
        else:
            if send_photo:
                message: Message = context.bot.send_photo(
                    chat_id=chat.id, photo=photos[0].media
                )
                message = [message.message_id]
                redis_helper.save("%s_photos_message" % user.id, str(message))
                logger.info(message)
            else:
                message = redis_helper.retrieve("%s_photos_message" % user.id).decode()
                if message:
                    message = eval(message)

            keyboard = build_view_wishlist_element_photos_keyboard(
                wishlist_element, message
            )
    if len(photos) == 10:
        text += WISHLIST_PHOTO_LIMIT_REACHED
    else:
        if append:
            text += append
    logger.info(text)
    if photos and send_photo:
        context.bot.send_message(
            chat_id=chat.id,
            text=text,
            reply_markup=keyboard,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    else:
        context.bot.edit_message_text(
            chat_id=chat.id,
            message_id=message_id,
            text=text,
            reply_markup=keyboard,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )


def extract_photo_from_message(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    delete_if_private(message)
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    photo: List[PhotoSize] = message.photo
    if photo:
        logger.info("Received compressed photo")
        photo: PhotoSize = max(photo, key=operator.attrgetter("file_size"))
        photo: str = photo.file_id
    if not photo:
        if message.document:
            print("Received not compressed photo")
            photo: str = message.document.file_id
    wish_id = redis_helper.retrieve("%s_%s" % (user.id, user.id)).decode()
    try:
        add_photo(wish_id, photo)
        redis_helper.save("%s_photo_reached" % (user.id), "false")
        message: str = SINGLE_WISHLIST_PHOTO_ADDED % 1
    except ValueError:
        status = redis_helper.retrieve("%s_photo_reached" % (user.id)).decode()
        if status == "true":
            return
        logger.info("photo limit reached")
        redis_helper.save("%s_photo_reached" % (user.id), "true")
        message: str = WISHLIST_PHOTO_LIMIT_REACHED
    logger.info("viewing wishlist_element with append")
    message_id = redis_helper.retrieve("%s_ask_photo_message" % user.id).decode()
    photo_sended: str = redis_helper.retrieve("%s_photo_sended" % user.id).decode()
    if not photo_sended.isnumeric():
        photo_sended = 1
    else:
        photo_sended = int(photo_sended)
        photo_sended += 1
    wishlist_element: WishlistElement = find_wishlist_element_by_id(wish_id)
    if len(wishlist_element.photos) == 10:
        messages = redis_helper.retrieve("%s_photos_message" % user.id)
        if messages:
            messages = messages.decode()
            messages = eval(messages)
            try:
                for message_id in messages:
                    context.bot.delete_message(chat_id=chat.id, message_id=message_id)
            except BadRequest:
                pass
        view_wishlist_element_photos(update, context, message)
        return ConversationHandler.END
    redis_helper.save("%s_photo_sended" % user.id, photo_sended)
    logger.info(message_id)
    text: str = REQUEST_WISHLIST_PHOTO
    text: str = REQUEST_WISHLIST_PHOTO % wishlist_element.description
    text = "%s\n\n%s" % (ASK_FOR_PHOTOS_PREPEND % len(wishlist_element.photos), text)
    messages = redis_helper.retrieve("%s_photos_message" % user.id)
    logger.info("extracted wish_id and mesasges")
    if messages:
        messages = messages.decode()
        messages = eval(messages)
    else:
        messages = []
    logger.info("deleting photo messages")
    try:
        for m in messages:
            context.bot.delete_message(chat_id=chat.id, message_id=m)
    except BadRequest:
        pass
    if wishlist_element.links:
        if extractor.extractor_exists(wishlist_element.links):
            if not extractor.validate_url(wishlist_element.links):
                text += MALFORMED_VALID_LINK_APPEND % wishlist_element.link
        else:
            text += NOT_SUPPORTED_LINK_APPEND % wishlist_element.link
    wishlist_id = get_current_wishlist_id(user.id)
    wishlist = find_wishlist_by_id(wishlist_id)
    title = f"{wishlist.title.upper()}  –  "
    text: str = f"{WISHLIST_HEADER % title}{text}"
    message: Message = context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        text=text,
        message_id=message_id,
        reply_markup=create_cancel_wishlist_element_photo_keyboard(
            wish_id,
            True,
            True,
            download_supported=extractor.is_supported(wishlist_element.links),
            link=wishlist_element.link,
        ),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
    return ADD_PHOTO


def ask_for_photo(update: Update, context: CallbackContext):
    logger.info("adding photo")
    message: Message = update.effective_message
    user: User = update.effective_user
    redis_helper.save("%s_photo_sended" % user.id, "0")
    wish_id = update.callback_query.data.split("_")[-1]
    wish_id_ = redis_helper.retrieve("%s_%s" % (user.id, user.id)).decode()
    page = update.callback_query.data.split("_")[-2]
    if not page.isnumeric():
        page = redis_helper.retrieve("%s_current_page" % user.id).decode()
    redis_helper.save("%s_current_page" % user.id, page)
    redis_helper.save("%s_%s" % (user.id, user.id), wish_id)
    wishlist_element: WishlistElement = find_wishlist_element_by_id(wish_id)
    text: str = REQUEST_WISHLIST_PHOTO % wishlist_element.description
    if wishlist_element.photos:
        text = "%s\n\n%s" % (
            ASK_FOR_PHOTOS_PREPEND % len(wishlist_element.photos),
            text,
        )
    else:
        wishlist_id = get_current_wishlist_id(user.id)
        wishlist = find_wishlist_by_id(wishlist_id)
        title = f"{wishlist.title.upper()}  –  "
        text: str = f"{WISHLIST_HEADER % title}{text}"
    if wishlist_element.links:
        if extractor.extractor_exists(wishlist_element.links):
            if not extractor.validate_url(wishlist_element.links):
                text += MALFORMED_VALID_LINK_APPEND % wishlist_element.link
        else:
            text += NOT_SUPPORTED_LINK_APPEND % wishlist_element.link
    # messages = redis_helper.retrieve("%s_photos_message" % user.id)
    # logger.info("extracted wish_id and mesasges")
    # if messages:
    #     messages = messages.decode()
    #     messages = eval(messages)
    # else:
    #     messages = []
    # logger.info("deleting photo messages")
    # try:
    #     for message_id in messages:
    #         context.bot.delete_message(chat_id=message.chat_id, message_id=message_id)
    # except BadRequest:
    #     pass
    message: Message = context.bot.edit_message_text(
        chat_id=message.chat_id,
        text=text,
        message_id=message.message_id,
        reply_markup=create_cancel_wishlist_element_photo_keyboard(
            wish_id,
            photos=wishlist_element.photos,
            page=page,
            download_supported=extractor.is_supported(wishlist_element.links),
            link=wishlist_element.link,
        ),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
    redis_helper.save("%s_ask_photo_message" % user.id, message.message_id)
    logger.info(message.message_id)
    return ADD_PHOTO


def cancel_add_photo(update: Update, context: CallbackContext):
    user: User = update.effective_user
    logger.info("CALLBACK DATA %s" % update.callback_query.data)
    if not "go_back" in update.callback_query.data:
        if not "sended" in update.callback_query.data:
            view_wishlist_element_photos(update, context, send_photo=False)
        else:
            view_wishlist_element_photos(update, context, send_photo=True)
    else:
        page = redis_helper.retrieve("%s_current_page" % user.id).decode()
        logger.info(f"THIS IS THE {page}")
        update.callback_query.data += "_%s" % page
        view_wishlist(update, context, reset_keyboard=False)
    return ConversationHandler.END


def download_photo_automatically(update: Update, context: CallbackContext):
    user: User = update.effective_user
    chat: Chat = update.effective_chat
    data: str = update.callback_query.data
    data = data.split("_")[-1]
    wishlist_element: WishlistElement = find_wishlist_element_by_id(data)
    pictures = extractor.load_url(wishlist_element.links)
    if wishlist_element.photos:
        for photo in wishlist_element.photos:
            if photo in pictures:
                pictures.remove(photo)
    pictures = pictures[:10]
    if len(wishlist_element.photos) == 0:
        wishlist_element.photos = pictures
    else:
        messages = redis_helper.retrieve("%s_photos_message" % user.id)
        if messages:
            messages = messages.decode()
            messages = eval(messages)
            try:
                for message_id in messages:
                    context.bot.delete_message(chat_id=chat.id, message_id=message_id)
            except BadRequest:
                pass
        total_left = 10 - len(wishlist_element.photos)
        pictures = pictures[:total_left]
        wishlist_element.photos = wishlist_element.photos + pictures
        wishlist_element.photos = (
            wishlist_element.photos[-1]
            if len(wishlist_element.photos) > 10
            else wishlist_element.photos
        )
    wishlist_element.save()
    view_wishlist_element_photos(update, context)
    return ConversationHandler.END


ADD_WISHLIST_PHOTO_CONVERSATION = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            ask_for_photo,
            pattern="ask_for_wishlist_element_photo",
        ),
    ],
    states={
        ADD_PHOTO: [
            MessageHandler(Filters.photo, extract_photo_from_message),
            CallbackQueryHandler(
                download_photo_automatically, pattern="auto_download_pictures"
            ),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(
            cancel_add_photo,
            pattern="cancel_add_photo",
        ),
        CallbackQueryHandler(
            cancel_add_photo,
            pattern="cancel_and_go_back",
        ),
    ],
)