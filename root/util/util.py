#!/usr/env python3

""" Various functions used across the project """

from random import randint
from re import sub
from base64 import b64decode
import re
from typing import List
from pyrogram.client import Client

from telegram_utils.utils.misc import environment
from root.contants.constant import FORMAT_ENTITIES, FORMAT_ENTITIES_TYPES
from root.helper.whitelist_helper import is_whitelisted
import sys
from telegram.message import Message
from telegram.user import User
from urlextract import URLExtract
import traceback
from xml.sax.saxutils import escape
from time import time
from os.path import split
from uuid import uuid4
import ast
import random
from os import environ
from datetime import datetime
from mongoengine import connect
from pymongo.mongo_client import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure
from pyrogram.types.messages_and_media import message_entity
from telegram import Message as TelegramMessage
from telegram import InlineKeyboardButton
from root.util.telegram import TelegramSender
import root.util.logger as logger
from root.contants.messages import (
    DB_CONNECTION_ERROR,
    DB_CONNECTION_SUCCESS,
    DB_GENERIC_ERROR,
    GROUP_NOT_ALLOWED,
    MESSAGE_DELETION_FUNNY_APPEND,
    MESSAGE_DELETION_TIMEOUT,
    MESSAGE_EDIT_TIMEOUT,
    RANDOM_ITEM_LIST,
)
import telegram_utils.helper.redis as redis_helper
from telegram import MessageEntity

extractor = URLExtract()
sender = TelegramSender()

long_month = {
    1: "Gennaio",
    2: "Febbraio",
    3: "Marzo",
    4: "Aprile",
    5: "Maggio",
    6: "Giugno",
    7: "Luglio",
    8: "Agosto",
    9: "Settembre",
    10: "Ottobre",
    11: "Novembre",
    12: "Dicembre",
    13: "E̵͙̦̓̔͘͜l̴̢͙͓̓̿͝u̴̝̼̫̔̔͘l̵͓͖̘͋̓̚",
}
short_month = {
    1: "Gen",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "Mag",
    6: "Giu",
    7: "Lug",
    8: "Ago",
    9: "Set",
    10: "Ott",
    11: "Nov",
    12: "Dic",
    13: "E̵͙̦̓̔͘͜l̴̢͙͓̓̿͝u̴̝̼̫̔̔͘l̵͓͖̘͋̓̚",
}

short_text_month = {
    "gen": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "mag": 5,
    "giu": 6,
    "lug": 7,
    "ago": 8,
    "set": 9,
    "ott": 10,
    "nov": 11,
    "dic": 12,
    "e̵̓l̴̓u̴̔l̵͋": 13,
}

long_text_month = {
    "gennaio": 1,
    "febbraio": 2,
    "marzo": 3,
    "aprile": 4,
    "maggio": 5,
    "giugno": 6,
    "luglio": 7,
    "agosto": 8,
    "settembre": 9,
    "ottobre": 10,
    "novembre": 11,
    "dicembre": 12,
    "e̵̓l̴̓u̴̔l̵͋": 13,
}


def generate_random_invisible_char(user_id):
    previous = redis_helper.retrieve("%s_%s_previous_value" % (user_id, user_id))
    if previous:
        previous = previous.decode()
        previous = int(previous)
    else:
        previous = 0
    n = randint(1, 10)
    while n == previous:
        n = randint(1, 10)
    redis_helper.save("%s_%s_previous_value" % (user_id, user_id), str(n))
    return "&#8203;" * n


def remove_url_from_text(message: Message):
    text = message.text if message.text else message.caption
    entities = [entity.url for entity in message.entities if entity.type == "text_link"]
    urls = extractor.find_urls(text)
    for url in urls:
        text = re.sub(url, "", text)
    for entity in entities:
        text = re.sub(entity, "", text)
    return text


def extract_first_link_from_message(message):
    text = message.text if message.text else message.caption
    entities = message.entities
    entity = next(
        entity
        for entity in entities
        if entity.type == "text_link" or entity.type == "url"
    )
    if entity:
        if entity.type == "url":
            urls = extractor.find_urls(text)
            logger.info(urls)
            if urls:
                return urls[0]
        else:
            return entity.url


def append_timeout_message(message: str, delete: bool, timeout: int, show_joke: bool):
    if delete:
        joke = ""
        if show_joke:
            if random.choice(range(100)) > 87:
                joke = random.choice(MESSAGE_DELETION_FUNNY_APPEND)
        message += MESSAGE_DELETION_TIMEOUT % (ttm(timeout), joke)
    else:
        message += MESSAGE_EDIT_TIMEOUT % (ttm(timeout))
    return message


def ttm(timeout: int):
    logger.info(f"parsing timeout {timeout}")
    seconds = timeout
    if timeout > 60:
        timeout = timeout // 60
        minute = "i" if timeout > 1 else "o"
        while seconds >= 60:
            seconds -= 60
        if not seconds > 0:
            return "%s %s" % (timeout, "minut%s" % minute)
        else:
            second = "i" if seconds > 1 else "o"
            return "%s %s e %s %s" % (
                timeout,
                "minut%s" % minute,
                seconds,
                "second%s" % second,
            )
    else:
        return "%s %s" % (timeout, "secondi")


def random_item():
    index = randint(0, len(RANDOM_ITEM_LIST) - 1)
    return RANDOM_ITEM_LIST[index]


def month_starts_with(month: str):
    """ check if the first 3 letters of the word is a valid message or not """
    month: str = month[:3]
    month: str = month.lower()
    if any(m for m in short_text_month if month == m):
        index: str = next(m for m in short_text_month if month == m)
        if index:
            index: int = short_text_month[index]
            try:
                return short_month[index].lower(), long_month[index].lower()
            except IndexError:
                return short_month[1].lower(), long_month[1].lower()
        return short_month[1].lower(), long_month[1].lower()
    return short_month[1].lower(), long_month[1].lower()


def get_month_number(month: str) -> int:
    """return the int of the month from a string

    Args:
        month (str): The month in string format

    Returns:
        int: the int
    """
    month = month.lower()
    if month in long_text_month.keys():
        return long_text_month[month]
    if month in short_text_month.keys():
        return short_text_month[month]


def is_text_month(month: str) -> bool:
    """Check if a string is a valid month

    Args:
        month (str): The string to check

    Returns:
        bool: If is a valid short or long month string
    """
    month = month.lower()
    return month in long_text_month.keys() or month in short_text_month.keys()


def format_date(date: datetime, show_year: bool = False, timezone: bool = False):
    if show_year:
        if timezone:
            date = date.astimezone()
            return date.strftime("%d/%m/%Y (%Z)")
        return date.strftime("%d/%m/%Y")
    else:
        if timezone:
            date = date.astimezone()
            return date.strftime("%d/%m (%Z)")
        return date.strftime("%d/%m")


def format_time(date: datetime, sec: bool = False):
    logger.info("formatting %s [%s]" % (date, type(date)))
    if not sec:
        return date.astimezone().strftime("%H:%M")
    else:
        return date.astimezone().strftime("%H:%M:%S")


def has_number(content: str) -> bool:
    """Check if a string contains a number

    Args:
        content (str): The string to parse

    Returns:
        bool: True if found, False otherwise
    """
    return any(char.isdigit() for char in content)


def is_number(content: str) -> bool:
    """Check if a string is a number

    Args:
        content (str): The string to check

    Returns:
        bool: True if is a number, False otherwise
    """
    try:
        int(content)
        return True
    except ValueError:
        return False


def max_length_error_format(content: str, allowed: int, split: int, link: str = None):
    boundary = len(content) - allowed
    content = content[:split]
    if link:
        stuff = '<a href="%s">' % link
        content = '<a href="%s">%s' % (link, content)
    content = [t for t in content]
    if link:
        content.insert(allowed + len(stuff), "</a>")
        content.insert(allowed + len(stuff) + 1, "<s>")
    else:
        content.insert(allowed, "</code><s>")
    content.append("</s>")
    content.insert(0, "<code>")
    logger.info("".join(content))
    return "".join(content)


def is_develop() -> bool:
    """Chek if the profile is set to develop

    Returns:
        bool: If the profile is set to develop
    """
    try:
        profile = retrieve_key("PROFILE")
        return profile == "develop"
    except KeyError:
        return False


def escape_value(value: object):
    """ convert any object to a str and escape it """
    return escape(str(value))


def html_to_markdown(message: str):
    message = re.sub(r"<\/?i>", "__", message)
    message = re.sub(r"<\/?b>", "**", message)
    message = re.sub(r"<\/?s>", "~~", message)
    message = re.sub(r"<\/?code>", "`", message)
    message = re.sub(r"<\/?pre>", "```", message)
    return message


def text_entities_to_html(message: str, entities=List[MessageEntity]):
    logger.info(entities)
    entities.reverse()
    for entity in entities:
        entity: MessageEntity = entity
        if entity.type in FORMAT_ENTITIES_TYPES:
            offset, length = entity.offset, entity.length
            to_replace = message[offset : offset + length]
            logger.info("[%s - %s - %s]" % (offset, length, to_replace))
            if entity.type != "text_link":
                to_replace = FORMAT_ENTITIES[entity.type] % to_replace
            else:
                to_replace = FORMAT_ENTITIES[entity.type] % (entity.url, to_replace)
            message = "%s%s%s" % (
                message[:offset],
                to_replace,
                message[offset + length :],
            )
            logger.info(message)
    return message


def format_error(error: Exception, user: User = None):
    """ format an exception showing the type, filename, line number and message """
    # extreact the information about the exception
    exc_type, _, exc_tb = sys.exc_info()
    # extreact the filename where the exception was raised
    logger.error(traceback.format_exc())
    logger.error(exc_tb.tb_frame.f_code.co_filename)
    file_name = split(exc_tb.tb_frame.f_code.co_filename)[1]
    # return a formatted message with the exception info
    if user:
        user_link = '<a href="tg://user?id=%s">%s</a>' % (user.id, user.id)
    else:
        user_link = "<code>User not found</code>"
    return (
        "<code>[#ultimiacquisti]</code>\n"
        f"<b>Da:</b>  {user_link}\n"
        f"<b>File:</b>  <code>{escape_value(file_name)}:{escape_value(exc_tb.tb_lineno)}</code>\n"
        f"<b>Tipo eccezione:</b>  <code>{escape_value(exc_type)}</code>\n"
        f"<b>Messaggio:</b>  <code>{escape_value(error)}</code>"
    )


def create_button(
    message: str, callback: str, query: str, url: str = None
) -> InlineKeyboardButton:
    """Create a Telegram Inline Button

    Args:
        message (str): The text to show
        callback (str): The callback that the button will use
        query (str): The query string of the button
        url(str)[Optional]: The url of the button (default: None)

    Returns:
        InlineKeyboardButton: The Telegram Inline Button to use
    """
    return InlineKeyboardButton(message, callback_data=callback, url=url)


def retrieve_telegram_user(user_id: int):
    api_id = environment("API_ID")
    api_hash = environment("API_HASH")
    client: Client = Client("retrieve_product", api_id=api_id, api_hash=api_hash)
    try:
        client.start()
        return client.get_users(user_id)
    except Exception as e:
        e = format_error(e)
        logger.error(e)
    finally:
        client.stop()


def get_article(current_date: datetime):
    article = "il "
    if current_date.day == 1:
        article = "l'"
    elif current_date.day == 8:
        article = "l'"
    elif current_date.day == 11:
        article = "l'"
    return article


def format_price(price: float, accept_zero: bool = True) -> str:
    """Convert a float value into a well formatted str price

    Args:
        price (float): The float to convert

    Returns:
        str: The price formatted
    """
    if not accept_zero:
        if not price:
            return
    price = ("%.2f" % price).replace(".", ",")
    price = str(price)
    price = price.split(",")
    if len(price) > 1:
        price[0] = "{0:,}".format(int(price[0])).replace(",", ".")
    else:
        price = "{0:,}".format(int(price)).replace(",", ".").replace(",", ".")
    return ",".join(price)


def is_group_allowed(chat_id: int) -> bool:
    """Check if a group is allowed to use the bot

    Args:
        chat_id (int): The Telegram chat_id of the group

    Returns:
       bool:  If the group has access to the bot
    """
    groups = ast.literal_eval(retrieve_key("GROUP_ID"))
    if not str(chat_id) in groups:
        token = retrieve_key("TOKEN")
        logger.warn(f"chat_id {chat_id} is not allowed")
        if not is_whitelisted(chat_id):
            sender.send_message(token, chat_id, GROUP_NOT_ALLOWED, parse_mode="HTML")
            return False
    return True


def de_html(data: object) -> str:
    """Remove html tags from string

    Args:
        data (object): The data with the tags
    Returns:
        str: The data without the tags
    """
    return sub("<.*?>|\n", "", str(data))


def generate_id() -> str:
    """generate and id like 020120201801-7f36cd4a-6dfa-4b35-83c7-61d2ab8dafe0

    Returns:
        [str]: the id generated
    """
    now = datetime.now()
    date = now.strftime("%m%d%Y%H%M")
    uuid = str(uuid4())
    return f"{date}-{uuid}"


def get_month_string(month: int, short: bool = True, lower: bool = False) -> str:
    """Convert an interger to his string representation

    Args:
        month (int): The number of the month to convert to string
        short (bool, optional): Return the short 3 letter version. Defaults to True.
        lower (bool, optional): Return the text in lowercase. Defaults to False.

    Returns:
        str: The string representation of the month
    """
    month = 12 if month < 1 else month
    month = 1 if month > 13 else month
    month = short_month[month] if short else long_month[month]
    return month.lower() if lower else month


def get_current_month(short: bool = True, lower: bool = False, number=False) -> object:
    """Return a string representation or an integer number of the current month

    Args:
        month (int): The number of the month to convert to string
        short (bool, optional): Return the short 3 letter version. Defaults to True.
        lower (bool, optional): Return the text in lowercase. Defaults to False.
        number (bool, False): Return the number of the current month as integer

    Returns:
        str: The string representation or the integer of the current month
    """
    date = datetime.now()
    if not number:
        return get_month_string(date.month, short, lower)
    return date.month


def get_current_year() -> int:
    """Return the current year

    Returns:
        int: The current year
    """
    date = datetime.now()
    return date.year


def retrieve_key(key: str, decode=False):
    """retrieve an environment variable

    Args:
        key ([str]): the key to retrieve
        decode (bool, optional): if the key should be base64 decoded. Defaults to False.

    Returns:
        [string]: the value or the environment variable
    """
    try:
        data = environ[key]
        if decode:
            return sub("\n", "", b64decode(data).decode())
        return data
    except KeyError:
        logger.error("unable to find env variable {}".format(key))
        return None


def format_deal_due_date(deal: datetime, today: datetime):
    difference = deal - today
    seconds = difference.seconds
    days = difference.days
    minutes = seconds // 60
    hours = seconds // 60 // 60
    message = " per "
    append = []
    ### PARSING DAYS ######################################
    if days > 0:
        if days > 1:
            append.append("altri %s giorni" % days)
        else:
            append.append("%s altro giorno" % days)
    ### PARSING HOURS #####################################
    if hours > 0:
        minutes -= hours * 60
        if hours > 1:
            if days > 0:
                append.append("%s ore" % hours)
            else:
                append.append("altre %s ore" % hours)
        else:
            if not days > 0:
                append.append("1 altra ora")
            else:
                append.append("1 ora")
    ### PARSING MINUTES ###################################
    if minutes > 0:
        if minutes > 1:
            if days > 0 or hours > 0:
                append.append("%s minuti" % minutes)
            else:
                append.append("altri %s minuti" % minutes)
        else:
            if days or hours:
                append.append("%s minuto" % minutes)
            else:
                append.append("%s altro minuto" % minutes)

    append = ", ".join(append)
    # replace last comma with a ' e '
    append = re.sub(r"(.*), ", r"\1 e ", append)
    message += append
    return message


def db_connect():
    """connect to the desire database"""
    username = retrieve_key("DBUSERNAME", False)
    password = retrieve_key("DBPASSWORD", False)
    admin = str(retrieve_key("TELEGRAM_BOT_ADMIN"))
    token = retrieve_key("TOKEN")
    host = retrieve_key("DBHOST", False)
    database = retrieve_key("DBNAME", False)
    connection = retrieve_key("CONNECTION", False)
    connection = connection.format(username, password, host, database)
    logger.info("connecting to db")
    try:
        client: MongoClient = connect(host=connection)
        # client = connect(DB, username=USERNAME, password=PASSWORD,
        # host=HOST, port=PORT)
        client.server_info()
        logger.info(DB_CONNECTION_SUCCESS)
        if not is_develop():
            sender.send_message(token, admin, DB_CONNECTION_SUCCESS)
    except ServerSelectionTimeoutError:
        logger.error(DB_CONNECTION_ERROR)
        sender.send_message(token, admin, DB_CONNECTION_ERROR)
    except OperationFailure:
        logger.error(DB_CONNECTION_ERROR)
        sender.send_message(token, admin, DB_CONNECTION_ERROR)
    except Exception as exception:
        logger.error(exception)
        sender.send_message(token, admin, DB_GENERIC_ERROR)
