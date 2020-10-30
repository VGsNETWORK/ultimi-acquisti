#!/usr/env python3

""" Various functions used across the project """

from re import sub
from base64 import b64decode
from uuid import uuid4
import ast
from os import environ
from datetime import datetime
from mongoengine import connect
from pymongo.mongo_client import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure
from telegram import InlineKeyboardButton
from root.util.telegram import TelegramSender
from root.util.logger import Logger
from root.contants.messages import (
    DB_CONNECTION_ERROR,
    DB_CONNECTION_SUCCESS,
    DB_GENERIC_ERROR,
    GROUP_NOT_ALLOWED,
)

logger = Logger()
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


def is_develop():
    """Chek if the profile is set to develop

    Returns:
        [type]: If the profile is set to develop
    """
    try:
        profile = retrieve_key("PROFILE")
        return profile == "develop"
    except KeyError:
        return False


def create_button(message: str, callback: str, query: str) -> InlineKeyboardButton:
    """Create a Telegram Inline Button

    Args:
        message (str): The text to show
        callback (str): The callback that the button will use
        query (str): The query string of the button

    Returns:
        InlineKeyboardButton: The Telegram Inline Button to use
    """
    logger.info(f"creating button {query}")
    return InlineKeyboardButton(message, callback_data=callback)


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
    if str(chat_id) in groups:
        return True
    else:
        token = retrieve_key("TOKEN")
        logger.warn(f"chat_id {chat_id} is not allowed")
        sender.send_message(token, chat_id, GROUP_NOT_ALLOWED)


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
    month = short_month[month] if short else long_month[month]
    return month.lower() if lower else month


def get_current_month(
    short: bool = True, lower: bool = False, number=False
) -> str / int:
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
