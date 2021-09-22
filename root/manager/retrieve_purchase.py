#!/usr/bin/env python3

from datetime import datetime
import re
from root.model.purchase import Purchase
from typing import List
from telegram.chat import Chat
from root.util.util import format_error, remove_url_from_text
from root.helper.user_helper import is_admin
from telegram import Update
from telegram.ext.callbackcontext import CallbackContext
from pyrogram import Client
from pyrogram.types.messages_and_media.message import Message
from telegram_utils.utils.misc import environment
from root.helper.purchase_helper import convert_to_float, find_by_message_id_and_chat_id
import telegram_utils.utils.logger as logger
import json


def add_purchase(client: Client, message: Message):
    if not message.from_user.is_bot:
        text: str = message.text if message.text else message.caption
        date: int = message.date
        date: datetime = datetime.fromtimestamp(date)
        price: float = 0.00
        title: str = ""
        logger.info("extracted message date %s" % date)
        if message.forward_from_chat or message.forward_from:
            return None
        if re.findall(r"(?i)#ultimiacquisti", text):
            text = remove_url_from_text(message)
            # remove the hashtag from the message
            text: str = text.replace("#ultimiacquisti", "")
            text: str = text.strip()
            # check for a date from the user
            regex_date: List[str] = re.findall(r"(\d{1,2}/\d{1,2}/(\d{4}|\d{2}))", text)
            # extract the date if present
            if regex_date:
                regex_date: str = regex_date[0]
                if isinstance(regex_date, tuple):
                    regex_date: str = regex_date[0]
                logger.info(regex_date)
                try:
                    date: datetime = datetime.strptime(regex_date, "%d/%m/%Y")
                except ValueError:
                    date: datetime = datetime.strptime(regex_date, "%d/%m/%y")
                text: str = text.replace(regex_date, "")
                text: str = text.strip()

            # check for a price from the user
            regex_price: List[str] = re.findall(
                r"(?:\s|^|€)\d+(?:[\.\',]\d{3})?(?:[\.,]\d{1,2})?", text
            )
            # extract the price if present
            if regex_price:
                regex_price: str = regex_price[0]
                price = regex_price
                price = price.strip().replace("€", "")
                price = convert_to_float(price)
                text: str = text.replace(regex_price, "")
                text: str = text.strip()

            # check for a title from the user
            regex_title: List[str] = re.findall(r"%.*%", text)
            if regex_title:
                regex_title: str = regex_title[0]
                title = regex_title
                text: str = text.replace(regex_title, "")
                text: str = text.strip()
            logger.info(
                "Saving message %s : %s" % (message.message_id, message.chat.id)
            )
            Purchase(
                user_id=message.from_user.id,
                price=price,
                message_id=message.message_id,
                chat_id=message.chat.id,
                description=title,
            ).save()
            return True
        return False


def check_message(message: Message, client: Client):
    message_id = message.message_id
    chat_id = message.chat.id
    if not find_by_message_id_and_chat_id(message_id, chat_id):
        if add_purchase(client, message):
            return True
    return False


def get_messages_for(chat_id: int, client: Client):
    purchases_added = {}
    chat: Chat = client.get_chat(chat_id)
    group_name = chat.title.split(" | ")[0]
    for message in client.search_messages(chat_id, query=r"#ultimiacquisti"):
        message: Message = message
        text: str = message.text if message.text else message.caption
        if text:
            if re.findall(r"(?i)#ultimiacquisti", text):
                purchase = check_message(message, client)
                if purchase:
                    user_id = message.from_user.id
                    first_name = message.from_user.first_name
                    user_id = str(user_id)
                    if user_id in purchases_added:
                        purchases_added[user_id]["purchases_added"] += 1
                    else:
                        purchases_added[user_id] = {}
                        purchases_added[user_id]["purchases_added"] = 1
                        purchases_added[user_id]["first_name"] = first_name
    append = (
        "Ecco il recap degli acquisti importati per il gruppo <i>%s</i>:\n" % group_name
    )
    if purchases_added:
        for user_id in purchases_added:
            first_name = purchases_added[user_id]["first_name"]
            total_purchases_added = purchases_added[user_id]["purchases_added"]
            append += '    –  <code>%s</code>  acquisti per <a href="tg://user?id=%s">%s</a>\n' % (
                total_purchases_added,
                user_id,
                first_name,
            )
    else:
        append += "\n<i>Non sono stati trovati acquisti da importare!</i>"
    return append


def update_purchases_for_chat(update: Update, context: CallbackContext):
    chat_type = update.effective_chat.type
    if chat_type == "private":
        return
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
    api_id = environment("API_ID")
    api_hash = environment("API_HASH")
    client: Client = Client("retrieve_product", api_id=api_id, api_hash=api_hash)
    try:
        client.start()
        chat_id = update.effective_chat.id
        append = get_messages_for(chat_id, client)
        log_channel = environment("ERROR_CHANNEL")
        context.bot.send_message(
            chat_id=log_channel,
            text=append,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except Exception as e:
        e = format_error(e, update.effective_user)
        logger.error(e)
    finally:
        client.stop()