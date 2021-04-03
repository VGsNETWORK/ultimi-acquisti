#!/usr/env python3

""" Various functions used across the project """

from random import randint
from re import sub
from base64 import b64decode
import sys
from types import TracebackType
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


def append_timeout_message(message: str, delete: bool, timeout: bool, show_joke: bool):
    if delete:
        joke = ""
        if show_joke:
            if random.choice(range(100)) > 70:
                joke = random.choice(MESSAGE_DELETION_FUNNY_APPEND)
        message += MESSAGE_DELETION_TIMEOUT % (ttm(timeout), joke)
    else:
        message += MESSAGE_EDIT_TIMEOUT % (ttm(timeout))
    return message


def ttm(timeout: int):
    if timeout > 60:
        timeout = timeout // 60
        minute = "i" if timeout > 1 else "o"
        return "%s %s" % (timeout, "minut%s" % minute)
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


def format_error(error: Exception):
    """ format an exception showing the type, filename, line number and message """
    # extreact the information about the exception
    exc_type, _, exc_tb = sys.exc_info()
    # extreact the filename where the exception was raised
    file_name = split(exc_tb.tb_frame.f_code.co_filename)[1]
    # return a formatted message with the exception info
    return (
        f"<b>Exception Type:</b>  <code>{escape_value(exc_type)}</code>\n"
        f"<b>File Name:</b>  <code>{escape_value(file_name)}</code>\n"
        f"<b>Line Number:</b>  <code>{escape_value(exc_tb.tb_lineno)}</code>\n"
        f"<b>Message:</b>  <code>{escape_value(error)}</code>"
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


def format_price(price: float) -> str:
    """Convert a float value into a well formatted str price

    Args:
        price (float): The float to convert

    Returns:
        str: The price formatted
    """
    price = ("%.2f" % price).replace(".", ",")
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
        sender.send_message(token, chat_id, GROUP_NOT_ALLOWED)
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
