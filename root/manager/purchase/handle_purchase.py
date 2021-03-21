#!usr/bin/env python3

""" File to handle a new or and edited purchase """

import re
from datetime import datetime

from pyrogram.types.bots_and_keyboards import reply_keyboard_markup
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
    NOT_MESSAGE_OWNER,
    ONLY_GROUP,
    PURCHASE_ADDED,
    PURCHASE_DATE_ERROR,
    PURCHASE_MODIFIED,
    PURCHASE_PRICE_HINT,
    PURCHASE_TITLE_HINT,
    PURCHASE_DATE_HINT,
    PURCHASE_HEADER_HINT,
    PURCHASE_EMPTY_TITLE_HINT,
    SESSION_ENDED,
)
from root.helper.purchase_helper import convert_to_float, create_purchase
from root.helper.user_helper import create_user, user_exists, retrieve_user
from root.util.telegram import TelegramSender
from root.util.util import create_button, has_number, is_group_allowed, retrieve_key
from root.contants.message_timeout import SERVICE_TIMEOUT
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
    if message.chat.type == "private":
        client.send_message(chat_id, text=ONLY_GROUP, parse_mode="HTML")
        return
    if not is_group_allowed(chat_id):
        return
    message_id = message.message_id
    user = message.from_user
    user_id: int = user.id
    add_message(message_id, user_id)
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
            (mdate for mdate in caption if ("/" in mdate and has_number(mdate))), None
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

        price = re.findall(r"\d+(?:[\.\',]\d{3})?(?:[\.,]\d{1,2})?", caption)
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
    if not result["error"]:
        add_purchase(user, price, message_id, chat_id, date, caption)
        if not custom_date_error:
            message = PURCHASE_ADDED if not message.edit_date else PURCHASE_MODIFIED
            append_message = "".join(append_message)
            if modelUser.show_purchase_tips:
                if append_message:
                    append_message = f"{PURCHASE_HEADER_HINT}{append_message}"
                message += append_message
        else:
            message = PURCHASE_DATE_ERROR % (
                user.id,
                message.from_user.username,
            )
    else:
        message = result["error"]
    keyboard = build_purchase_keyboard(modelUser)
    sender.send_and_deproto(client, chat_id, message, keyboard, message_id, timeout=120)


def build_purchase_keyboard(user: UserModel):
    show_tips = user.show_purchase_tips
    message: str = "🙈  Nascondi suggerimenti" if show_tips else "🙉  Mostra suggerimenti"
    return InlineKeyboardMarkup(
        [[create_button(message, "purchase.toggle_tips", "purchase.toggle_tips")]]
    )


def toggle_purchase_tips(update: Update, context: CallbackContext):
    callback_query: CallbackQuery = update.callback_query
    message: Message = callback_query.message
    chat_id: int = message.chat.id
    logger.info(chat_id)
    message_id = message.message_id
    user: User = update.effective_user
    user_id: int = user.id
    try:
        if is_owner(message_id, user_id):
            context.bot.answer_callback_query(callback_query.id)
            modelUser: UserModel = retrieve_user(user_id)
            modelUser.show_purchase_tips = not modelUser.show_purchase_tips
            modelUser.save()
            keyboard = build_purchase_keyboard(modelUser)
            context.bot.edit_message_text(
                message_id=message_id,
                chat_id=chat_id,
                text="✅  <i>Impostazioni aggiornate con successo!</i>",
                reply_markup=keyboard,
                parse_mode="HTML",
            )
        else:
            context.bot.answer_callback_query(
                callback_query.id,
                text="❌  Non puoi modificare le impostazioni di un altro utente!",
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
