#!usr/bin/env python3

import re
from datetime import datetime
from pyrogram.types import Message
from root.util.logger import Logger
from pyrogram import Client, filters
from root.util.util import is_group_allowed
from pyrogram.handlers import MessageHandler
from root.util.telegram import TelegramSender
from root.helper.purchase_helper import create_purchase
from root.helper.purchase_helper import convert_to_float
from root.helper.user_helper import user_exists, create_user
from root.contants.messages import (
    ONLY_GROUP,
    PURCHASE_MODIFIED,
    PURCHASE_DATE_ERROR,
    PURCHASE_ADDED,
)

logger = Logger()


def add_purchase(user, price, message_id, chat_id, creation_date=None):
    if not user_exists(user.id):
        create_user(user)
    create_purchase(user.id, price, message_id, chat_id, creation_date)


def handle_purchase(client: Client, message: Message):
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
    caption = message.caption if message.caption else message.text
    logger.info("Parsing purchase")
    try:
        """
        regex: \d+(?:[\.\',]\d{3})?(?:[\.,]\d{1,2}|[\.,]\d{1,2})?
        \d      -> matches a number
        +       -> match one or more of the previous
        ()      -> capturing group
        ?:      -> do not create a capture group (makes no sense but it does not work without)
        [\.\',] -> matches . , '
        \d{3}   -> matches 3 numbers
        ?       -> makes the capturing group optional
        ()      -> capturing group
        ?:      -> do not create a capture group (makes no sense but it does not work without)
        [\.,]   -> marches . or ,
        \d{1,2} -> matches one or two numbers
        ?       -> makes the capturing group optional
        """
        price = re.findall(r"\d+(?:[\.\',]\d{3})?(?:[\.,]\d{1,2})?", caption)
        price = price[0] if len(price) != 0 else 0.00
        if price:
            price = convert_to_float(price)
            result = {"name": caption, "price": price, "error": None}
            logger.info(f"The user purchase {price} worth of products")
        else:
            result = {"name": caption, "price": 0.00, "error": None}
    except ValueError as ve:
        logger.error(ve)
        sender.send_to_log(ve)
        return
    except IndexError as ie:
        logger.error(ie)
        sender.send_to_log(ie)
        return
    mdate = re.findall(r"(\d(\d)?\/\d(\d)?\/\d{2}(\d{2})?)", caption)
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
        add_purchase(user, price, message_id, chat_id, date)
        if not custom_date_error:
            message = PURCHASE_ADDED if not message.edit_date else PURCHASE_MODIFIED
        else:
            message = PURCHASE_DATE_ERROR % (
                user.id,
                message.from_user.username,
            )
    else:
        message = result["error"]
    client.send_message(
        chat_id=chat_id,
        text=message,
        reply_to_message_id=message_id,
        parse_mode="HTML",
    )