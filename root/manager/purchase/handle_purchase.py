#!usr/bin/env python3

""" File to handle a new or and edited purchase """

import re
from datetime import datetime
from pyrogram import Client
from pyrogram.client import User
from pyrogram.types import Message
import root.util.logger as logger
from root.contants.messages import (
    ONLY_GROUP,
    PURCHASE_ADDED,
    PURCHASE_DATE_ERROR,
    PURCHASE_MODIFIED,
)
from root.helper.purchase_helper import convert_to_float, create_purchase
from root.helper.user_helper import create_user, user_exists
from root.util.telegram import TelegramSender
from root.util.util import has_number, is_group_allowed, retrieve_key

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
    if not user_exists(user.id):
        create_user(user)
    caption = message.caption if message.caption else message.text
    logger.info("Parsing purchase")
    try:
        # regex: \d+(?:[\.\',]\d{3})?(?:[\.,]\d{1,2}|[\.,]\d{1,2})?
        # \d      -> matches a number
        # +       -> match one or more of the previous
        # ()      -> capturing group
        # ?:      -> do not create a capture group (makes no sense but it does not work without)
        # [\.\',] -> matches . , '
        # \d{3}   -> matches 3 numbers
        # ?       -> makes the capturing group optional
        # ()      -> capturing group
        # ?:      -> do not create a capture group (makes no sense but it does not work without)
        # [\.,]   -> marches . or ,
        # \d{1,2} -> matches one or two numbers
        # ?       -> makes the capturing group optional

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

        price = re.findall(r"\d+(?:[\.\',]\d{3})?(?:[\.,]\d{1,2})?", caption)
        if len(price) != 0:
            caption = caption.split(" ")
            caption.remove(price[0])
            caption = " ".join(caption)
        price = price[0] if len(price) != 0 else 0.00
        price = convert_to_float(price)
        caption = re.findall(r"%.*%", caption)
        if caption:
            caption = caption[0]
            caption = caption[1:-1]
            caption = caption[:100]
        else:
            caption = ""
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
    if not result["error"]:
        add_purchase(user, price, message_id, chat_id, date, caption)
        if not custom_date_error:
            message = PURCHASE_ADDED if not message.edit_date else PURCHASE_MODIFIED
        else:
            message = PURCHASE_DATE_ERROR % (
                user.id,
                message.from_user.username,
            )
    else:
        message = result["error"]
    sender.send_and_deproto(client, chat_id, message, message_id, timeout=10)
