#!usr/bin/env python3

""" File to handle a new or and edited purchase """

import random
import re
from datetime import datetime

from telegram import chat
from root.manager.start import back_to_the_start
from telegram import message

from telegram.chat import Chat
from root.contants.keyboard import (
    ADD_PURCHASE_KEYBOARD,
    NEW_PURCHASE_FORMAT,
    NEW_PURCHASE_LINK,
    NEW_PURCHASE_TEMPLATE,
    NO_PURCHASE_KEYBOARD,
    create_wrong_date_keyboard,
    send_command_to_group_keyboard,
)
from root.model.purchase import Purchase

from root.helper.redis_message import add_message, is_owner
from pyrogram import Client
from pyrogram.client import User
from pyrogram.types import Message
from telegram.callbackquery import CallbackQuery
from telegram.ext.callbackcontext import CallbackContext
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.update import Update
import root.util.logger as logger
from root.contants.messages import (
    CANNOT_MODIFY_OTHERS_SETTINGS,
    MESSAGE_DELETION_FUNNY_APPEND,
    MESSAGE_DELETION_TIMEOUT,
    ONLY_GROUP_NO_QUOTE,
    PURCHASE_ADDED,
    PURCHASE_DATE_ERROR,
    PURCHASE_DISCARDED,
    PURCHASE_HINT_NO_HINT,
    PURCHASE_MODIFIED,
    PURCHASE_MODIFIED_DATE_ERROR,
    PURCHASE_PRICE_HINT,
    PURCHASE_RECAP_APPEND,
    PURCHASE_TITLE_HINT,
    PURCHASE_DATE_HINT,
    PURCHASE_HEADER_HINT,
    PURCHASE_EMPTY_TITLE_HINT,
    SESSION_ENDED,
)
from root.helper.process_helper import create_process, restart_process, stop_process
from root.helper.purchase_helper import (
    convert_to_float,
    create_purchase,
    delete_purchase,
    find_by_message_id_and_chat_id,
)
from root.helper.user_helper import create_user, user_exists, retrieve_user
from root.util.telegram import TelegramSender
from root.util.util import (
    append_timeout_message,
    create_button,
    format_price,
    has_number,
    is_group_allowed,
    is_number,
    retrieve_key,
    ttm,
)
from root.contants.message_timeout import LONG_SERVICE_TIMEOUT, ONE_MINUTE, TWO_MINUTES
from root.model.user import User as UserModel

sender = TelegramSender()


def add_purchase(
    user: User,
    price: float,
    message_id: float,
    chat_id: float,
    creation_date: datetime = None,
    caption: str = "",
) -> None:
    """add a new purchase

    Args:
        user (User): The user who purchased the item
        price (float): The price of the item
        message_id (float): The message_id of the post
        chat_id (float): The chat where the post was made
        creation_date (datetime, optional): The creation_date of the post. Defaults to None.
        caption (str, optional): The description of the purchase. Defaults to ''.
    """
    if not user_exists(user.id):
        create_user(user)
    create_purchase(user.id, price, message_id, chat_id, creation_date, caption)


def handle_purchase(client: Client, message: Message) -> None:
    """handle a new or a modified purchase

    Args:
        client (Client): The bot who recevied the update
        message (Message): The message received
    """
    if message.forward_from:
        return
    original_message = message
    edited = message.edit_date
    append_message = ["", "", ""]
    if message.from_user.is_bot:
        return
    token = retrieve_key("TOKEN")
    log_channel = retrieve_key("ERROR_CHANNEL")
    custom_date_error = False
    logger.info("Received message from mtproto")
    caption = message.caption if message.caption else message.text
    if not "#ultimiacquisti" in caption:
        return
    if message.edit_date:
        date = datetime.fromtimestamp(message.date)
        logger.info(f"formatted date {date}")
    else:
        date = None
    chat_id = message.chat.id
    message_id = message.message_id
    user = message.from_user
    user_id: int = user.id
    if not user_exists(user_id):
        create_user(user)
    caption = message.caption if message.caption else message.text
    logger.info("Parsing purchase")
    try:
        # regex: \d+(?:[\.\',]\d{3})?(?:[\.,]\d{1,2}|[\.,]\d{1,2})?
        # \d      -> matches a number
        # +       -> match one or more of the previous
        # ()      -> capturing groappend = ""up
        # ?:      -> do not create a capture group (makes no sense but it does not work without)
        # [\.\',] -> matches . , '
        # \d{3}   -> matches 3 numbers
        # ?       -> makes the capturing group optional
        # ()      -> capturing group
        # ?:      -> do not create a capture group (makes no sense but it does not work without)
        # [\.,]   -> marches . or ,
        # \d{1,2} -> matches one or two numbers
        # ?       -> makes the capturing group optional
        caption = caption.replace("\n", " ")
        caption = caption.split(" ")
        caption.remove("#ultimiacquisti")
        mdate = next(
            (
                mdate
                for mdate in caption
                if (
                    re.findall(r"(\d{1,2}/\d{1,2}/\d{2}|\d{4})", mdate)
                    and has_number(mdate)
                )
            ),
            None,
        )
        if mdate:
            caption.remove(mdate)
        else:
            mdate = "NO_DATE_TO_PARSE"
        caption = " ".join(caption)
        title = re.findall(r"%.*%", caption)
        if title:
            title = title[0]
            caption = caption.replace(title, "")
            title = title[1:-1]
            title = title[:100]
            if not title:
                title = "&lt;vuoto&gt;"
                append_message[2] = PURCHASE_EMPTY_TITLE_HINT
        else:
            title = ""
            append_message[2] = PURCHASE_TITLE_HINT
        logger.info(caption)
        price = re.findall(r"\d+(?:[\.\',]\d{3})?(?:[\.,]\d{1,2})?", caption)
        logger.info(price)
        original_price = price
        if len(price) == 0:
            append_message[0] = PURCHASE_PRICE_HINT
        price = price[0] if len(price) != 0 else "0.00"
        price = convert_to_float(price)
        caption = title
        result = {"name": caption, "price": price, "error": None}
        logger.info(f"The user purchase {price} worth of products")
        logger.info(result)
    except ValueError as value_error:
        logger.error(value_error)
        sender.send_message(token, log_channel, value_error)
        return
    except IndexError as index_error:
        logger.error(index_error)
        sender.send_message(token, log_channel, index_error)
        return
    mdate = re.findall(r"(\d(\d)?\/\d(\d)?\/\d{2}(\d{2})?)", mdate)
    mdate = mdate[0] if len(mdate) != 0 else None
    if mdate:
        cdate = datetime.now()
        mdate = mdate[0]
        try:
            if date:
                mtime = f"{date.hour}:{date.minute}:{date.second}"
            else:
                mtime = f"{cdate.hour}:{cdate.minute}:{cdate.second}"
            mdate = datetime.strptime(f"{mdate} {mtime}", "%d/%m/%Y %H:%M:%S")
        except ValueError:
            try:
                if date:
                    mtime = f"{date.hour}:{date.minute}:{date.second}"
                else:
                    mtime = f"{cdate.hour}:{cdate.minute}:{cdate.second}"
                mdate = datetime.strptime(f"{mdate} {mtime}", "%d/%m/%y %H:%M:%S")
            except ValueError:
                mdate = None
        if mdate:
            if mdate > cdate:
                custom_date_error = True
            else:
                date = mdate
        else:
            custom_date_error = True
    else:
        append_message[1] = PURCHASE_DATE_HINT
    modelUser: UserModel = retrieve_user(user_id)
    if modelUser.show_purchase_tips:
        # extract the elements that are not empty
        more_time = [m for m in append_message if m]
        append_timeout = 30 * len(more_time)
    else:
        append_timeout = 0
    ####################################
    if original_message.chat.type == "private":
        sender.delete_previous_message(
            message.from_user.id, message.message_id + 1, chat_id, None
        )
        message = ONLY_GROUP_NO_QUOTE % "#ultimiacquisti"
        price = price if price else "%3Cprezzo%3E"
        if is_number(price):
            original_price = price
            price = str(price)
            if "." in price:
                price = price.split(".")
                if int(price[1]) == 0:
                    price = str(price[0])
                    price += ",00%20%E2%82%AC"
                else:
                    price = str(original_price)
                    price = price.replace(".", ",")
                    if len(price.split(",")[1]) == 1:
                        price += "0%20%E2%82%AC"

        logger.info(f"THIS IS THE {date}")
        date = date if not isinstance(date, str) else "%3CDD%2FMM%2FYYYY%3E"
        date = date if date else "%3CDD%2FMM%2FYYYY%3E"
        caption = caption if caption else "%3Ctitolo%3E"
        if not isinstance(date, str):
            date = date.strftime("%d/%m/%Y")
        command = NEW_PURCHASE_FORMAT.format(price, date, caption)
        keyboard = send_command_to_group_keyboard(command, command_only=True)
        sender.send_and_proedit(
            chat_id,
            original_message,
            message,
            back_to_the_start,
            keyboard,
            timeout=ONE_MINUTE,
            append=True,
            create_redis=True,
        )
        return
    if not is_group_allowed(chat_id):
        return
    ####################################
    if not result["error"]:
        add_purchase(user, price, message_id, chat_id, date, caption)
        if not custom_date_error:
            message = PURCHASE_ADDED if not message.edit_date else PURCHASE_MODIFIED
            date = datetime.now() if not date else date
            message += PURCHASE_RECAP_APPEND(
                format_price(price),
                title,
                date,
                not len(original_price),
                False,
                not mdate,
            )
            append_message = "".join(append_message)
            if modelUser.show_purchase_tips:
                if append_message:
                    append_message = f"{PURCHASE_HEADER_HINT}{append_message}"
                else:
                    append_message = PURCHASE_HINT_NO_HINT
                message += append_message
        else:
            if edited:
                message = PURCHASE_MODIFIED_DATE_ERROR % (
                    user.id,
                    user.first_name,
                )
            else:
                message = PURCHASE_DATE_ERROR % (
                    user.id,
                    user.first_name,
                )
    else:
        message = result["error"]
    if custom_date_error:
        keyboard = create_wrong_date_keyboard(message_id, edited)
    else:
        keyboard = build_purchase_keyboard(modelUser)
    logger.info(ONE_MINUTE + append_timeout)
    add_message(message_id=message_id, user_id=user_id, add=False)
    if original_message.chat.type != "private":
        sender.send_and_deproto(
            client,
            chat_id,
            message,
            keyboard,
            message_id,
            create_redis=True,
            user_id=user_id,
            timeout=ONE_MINUTE + append_timeout,
            show_timeout=not custom_date_error,
        )
    else:
        logger.info("command from a private chat")
        sender.send_and_edit(
            None, None, chat_id, message, back_to_the_start, timeout=ONE_MINUTE
        )
    if custom_date_error:
        stop_process(message_id + 1)


def build_purchase_keyboard(user: UserModel):
    show_tips = user.show_purchase_tips
    message: str = "🙈  Nascondi suggerimenti" if show_tips else "🙉  Mostra suggerimenti"
    return InlineKeyboardMarkup(
        [[create_button(message, "purchase.toggle_tips", "purchase.toggle_tips")]]
    )


def toggle_purchase_tips(update: Update, context: CallbackContext):
    total_tips = 0
    price = 0.00
    date = None
    title = None
    callback_query: CallbackQuery = update.callback_query
    message: Message = callback_query.message
    chat_id: int = message.chat.id
    message_id = message.message_id
    reply_message: Message = message.reply_to_message
    caption: str = (
        reply_message.caption if reply_message.caption else reply_message.text
    )
    user: User = update.effective_user
    user_id: int = user.id
    purchase_service_message: str = (
        PURCHASE_MODIFIED if reply_message.edit_date else PURCHASE_ADDED
    )
    try:
        if is_owner(message_id, user_id):
            message: str = ""
            purchase: Purchase = find_by_message_id_and_chat_id(
                reply_message.message_id, chat_id
            )
            if purchase:
                if not purchase.price:
                    logger.info("Adding price hint")
                    message = PURCHASE_PRICE_HINT
                    total_tips += 1
                else:
                    price = purchase.price
                caption = caption.replace("\n", " ")
                caption = caption.split(" ")
                caption.remove("#ultimiacquisti")
                # fmt: off
                mdate = next(
                    (mdate for mdate in caption if ("/" in mdate and has_number(mdate))),
                    None)
                # fmt: on
                if not mdate:
                    logger.info("Adding date hint")
                    message += PURCHASE_DATE_HINT
                    total_tips += 1
                else:
                    try:
                        date = datetime.strptime(mdate, "%d/%m/%y")
                    except ValueError:
                        date = datetime.strptime(mdate, "%d/%m/%Y")
                if not purchase.description:
                    logger.info("Adding title hint")
                    message += PURCHASE_TITLE_HINT
                    total_tips += 1
                else:
                    title = purchase.description
                if message:
                    logger.info("Adding setting the header hint")
                    message = f"{PURCHASE_HEADER_HINT}{message}"
                else:
                    message = PURCHASE_HINT_NO_HINT
                context.bot.answer_callback_query(callback_query.id)
                modelUser: UserModel = retrieve_user(user_id)
                modelUser.show_purchase_tips = not modelUser.show_purchase_tips
                if modelUser.show_purchase_tips:
                    append_timeout = 30 * total_tips
                else:
                    append_timeout = 0
                if not restart_process(message_id, ONE_MINUTE + append_timeout):
                    create_process(
                        name_prefix=message_id,
                        target=sender.delete_message,
                        args=(None, chat_id, message_id, ONE_MINUTE + append_timeout),
                    )
                date = datetime.now() if not date else date
                recap_message = PURCHASE_RECAP_APPEND(
                    format_price(price),
                    title,
                    date,
                    not purchase.price,
                    False,
                    not mdate,
                )
                if modelUser.show_purchase_tips:
                    logger.info("Sending message with tips")
                    message = f"{purchase_service_message}{recap_message}{message}"
                else:
                    logger.info("Sending message without tips")
                    message = f"{purchase_service_message}{recap_message}"
                modelUser.save()
                keyboard = build_purchase_keyboard(modelUser)
                if random.choice(range(100)) > 87:
                    message += MESSAGE_DELETION_TIMEOUT % (
                        ttm(ONE_MINUTE + append_timeout),
                        random.choice(MESSAGE_DELETION_FUNNY_APPEND),
                    )
                else:
                    message += MESSAGE_DELETION_TIMEOUT % (
                        ttm(ONE_MINUTE + append_timeout),
                        "",
                    )
                context.bot.edit_message_text(
                    message_id=message_id,
                    chat_id=chat_id,
                    text=message,
                    reply_markup=keyboard,
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                )
        else:
            context.bot.answer_callback_query(
                callback_query.id,
                text=CANNOT_MODIFY_OTHERS_SETTINGS,
                show_alert=True,
            )
    except ValueError as e:
        logger.error(e)
        context.bot.answer_callback_query(
            callback_query.id,
            text=SESSION_ENDED,
            show_alert=True,
        )
        sender.delete_message(context, chat_id, message_id)


def confirm_purchase(update: Update, context: CallbackContext):
    callback: CallbackQuery = update.callback_query
    query: str = callback.data
    message_to_edit = int(query.split("_")[-1])
    user: User = update.effective_user
    user_id: int = user.id
    chat: Chat = update.effective_chat
    message: Message = update.effective_message
    message_id: int = message.message_id
    chat_id: int = chat.id
    modelUser: UserModel = retrieve_user(user_id)
    modelUser.show_purchase_tips = not modelUser.show_purchase_tips
    modelUser.save()
    if is_owner(message_to_edit, user_id):
        context.bot.answer_callback_query(callback.id)
        logger.info(f"editing message {message_id} on chat {chat_id}")
        toggle_purchase_tips(update, context)
    else:
        context.bot.answer_callback_query(
            callback.id,
            text=CANNOT_MODIFY_OTHERS_SETTINGS,
            show_alert=True,
        )


def discard_purchase(update: Update, context: CallbackContext):
    callback: CallbackQuery = update.callback_query
    query: str = callback.data
    message_to_delete = int(query.split("_")[-1])
    user: User = update.effective_user
    user_id: int = user.id
    message: Message = update.effective_message
    message_id: int = message.message_id
    chat: Chat = update.effective_chat
    chat_id: int = chat.id
    if is_owner(message_to_delete, user_id):
        logger.info(f"deleting message {message_id} on chat {chat_id}")
        context.bot.answer_callback_query(callback.id)
        delete_purchase(user_id=user_id, message_id=message_to_delete)
        context.bot.delete_message(chat_id=chat_id, message_id=message_to_delete)
        create_process(
            name_prefix=message.message_id,
            target=sender.delete_message,
            args=(None, chat_id, message.message_id, LONG_SERVICE_TIMEOUT),
        )
        try:
            message = append_timeout_message(
                PURCHASE_DISCARDED, True, LONG_SERVICE_TIMEOUT, True
            )
            context.bot.edit_message_text(
                chat_id=chat_id,
                text=message,
                message_id=message_id,
                reply_markup=ADD_PURCHASE_KEYBOARD,
                parse_mode="HTML",
            )
        except Exception as e:
            logger.error(e)
    else:
        context.bot.answer_callback_query(
            callback.id,
            text=CANNOT_MODIFY_OTHERS_SETTINGS,
            show_alert=True,
        )
