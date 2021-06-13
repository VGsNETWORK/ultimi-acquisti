#!/usr/bin/env python3

from root.contants.messages import (
    REQUEST_WISHLIST_PHOTO,
    SINGLE_WISHLIST_PHOTO_ADDED,
    VIEW_WISHLIST_PHOTO_MESSAGE,
    VIEW_NO_WISHLIST_PHOTO_MESSAGE,
    WISHLIST_PHOTO_LIMIT_REACHED,
)
from telegram.error import BadRequest
from root.manager.whishlist import view_wishlist
from root.contants.keyboard import (
    build_view_wishlist_photos_keyboard,
    create_cancel_wishlist_photo_keyboard,
)
from telegram.chat import Chat
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.ext.conversationhandler import ConversationHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram.files.inputmedia import InputMediaPhoto
from root.model.wishlist import Wishlist
from root.helper.wishlist import add_photo, find_wishlist_by_id, remove_photo
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


def delete_wishlist_photo(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    message_id = update.callback_query.data.split("_")[-1]
    context.bot.delete_message(chat_id=message.chat_id, message_id=message_id)
    wish_id = redis_helper.retrieve("%s_%s" % (user.id, user.id)).decode()
    wishlist: Wishlist = find_wishlist_by_id(wish_id)
    photos: List[str] = wishlist.photos
    messages = redis_helper.retrieve("%s_photos_message" % user.id)
    if messages:
        messages = messages.decode()
        messages: List[str] = eval(messages)
    else:
        messages = []
    messages = [str(m) for m in messages]
    logger.info(messages)
    logger.info(message_id)
    index = messages.index(str(message_id))
    photo = photos[index]
    photos.remove(photo)
    wishlist.photos = photos
    remove_photo(wish_id, photo)
    messages.remove(str(message_id))
    redis_helper.save("%s_photos_message" % user.id, str(messages))
    if not photos:
        text: str = VIEW_NO_WISHLIST_PHOTO_MESSAGE % (wishlist.description)
        keyboard = build_view_wishlist_photos_keyboard(wishlist, [])
    else:
        text = VIEW_WISHLIST_PHOTO_MESSAGE % (
            len(wishlist.photos),
            wishlist.description,
        )
        keyboard = build_view_wishlist_photos_keyboard(wishlist, messages)
    context.bot.edit_message_text(
        chat_id=chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=keyboard,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


def delete_photos_and_go_to_wishlist(update: Update, context: CallbackContext):
    user: User = update.effective_user
    message: Message = update.effective_message
    messages = redis_helper.retrieve("%s_photos_message" % user.id)
    if messages:
        messages = messages.decode()
        messages = eval(messages)
        try:
            for message_id in messages:
                context.bot.delete_message(
                    chat_id=message.chat_id, message_id=message_id
                )
        except BadRequest:
            pass
    data = update.callback_query.data
    page = redis_helper.retrieve("%s_current_page" % user.id).decode()
    redis_helper.save(user.id, message.message_id)
    logger.info("THIS NEEDS TO BE EDITED %s " % message.message_id)
    if not page:
        page: str = data.split("_")[-1]
    logger.info("%s this is the page" % page)
    view_wishlist(update, context, page=int(page))


def view_wishlist_photos(update: Update, context: CallbackContext, append: str = None):
    message: Message = update.effective_message
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    message_id = redis_helper.retrieve("%s_ask_photo_message" % user.id).decode()
    message_id = message_id if append else message.message_id
    if update.callback_query:
        data: str = update.callback_query.data
        wish_id: str = data.split("_")[-1]
        page: str = data.split("_")[-2]
        if not page.isnumeric():
            page = redis_helper.retrieve("%s_current_page" % user.id).decode()
        redis_helper.save("%s_current_page" % user.id, page)
    else:
        wish_id = redis_helper.retrieve("%s_%s" % (user.id, user.id)).decode()
    redis_helper.save("%s_%s" % (user.id, user.id), wish_id)
    wishlist: Wishlist = find_wishlist_by_id(wish_id)
    photos: List[str] = wishlist.photos
    if not photos:
        text: str = VIEW_NO_WISHLIST_PHOTO_MESSAGE % (wishlist.description)
        keyboard = build_view_wishlist_photos_keyboard(wishlist, [])
    else:
        logger.info(message_id)
        context.bot.delete_message(chat_id=message.chat_id, message_id=message_id)
        text = VIEW_WISHLIST_PHOTO_MESSAGE % (
            len(wishlist.photos),
            wishlist.description,
        )
        logger.info("sending %s photos" % len(photos))
        photos = [InputMediaPhoto(media=photo) for photo in photos]
        if len(photos) > 1:
            message: List[Message] = context.bot.send_media_group(
                chat_id=chat.id, media=photos
            )
            message = [m.message_id for m in message]
            keyboard = build_view_wishlist_photos_keyboard(wishlist, message)
        else:
            message: Message = context.bot.send_photo(
                chat_id=chat.id, photo=photos[0].media
            )
            message = [message.message_id]
            keyboard = build_view_wishlist_photos_keyboard(wishlist, message)
        redis_helper.save("%s_photos_message" % user.id, str(message))
    if len(photos) == 10:
        text += WISHLIST_PHOTO_LIMIT_REACHED
    else:
        if append:
            text += append
    logger.info(text)
    if photos:
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
    logger.info("viewing wishlist with append")
    view_wishlist_photos(update, context, message)
    return ConversationHandler.END


def ask_for_photo(update: Update, context: CallbackContext):
    logger.info("adding photo")
    message: Message = update.effective_message
    user: User = update.effective_user
    text: str = REQUEST_WISHLIST_PHOTO
    wish_id = redis_helper.retrieve("%s_%s" % (user.id, user.id)).decode()
    messages = redis_helper.retrieve("%s_photos_message" % user.id)
    logger.info("extracted wish_id and mesasges")
    if messages:
        messages = messages.decode()
        messages = eval(messages)
    else:
        messages = []
    logger.info("deleting photo messages")
    try:
        for message_id in messages:
            context.bot.delete_message(chat_id=message.chat_id, message_id=message_id)
    except BadRequest:
        pass
    logger.info("editing message")
    message: Message = context.bot.edit_message_text(
        chat_id=message.chat_id,
        text=text,
        message_id=message.message_id,
        reply_markup=create_cancel_wishlist_photo_keyboard(wish_id),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
    redis_helper.save("%s_ask_photo_message" % user.id, message.message_id)
    logger.info(message.message_id)
    return ADD_PHOTO


def cancel_add_photo(update: Update, context: CallbackContext):
    view_wishlist_photos(update, context)
    return ConversationHandler.END


ADD_WISHLIST_PHOTO_CONVERSATION = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            ask_for_photo,
            pattern="ask_for_wishlist_photo",
        ),
    ],
    states={
        ADD_PHOTO: [MessageHandler(Filters.photo, extract_photo_from_message)],
    },
    fallbacks=[
        CallbackQueryHandler(
            cancel_add_photo,
            pattern="cancel_add_photo",
        ),
    ],
)