#!/usr/env python3

from re import sub
from base64 import b64decode
from uuid import uuid4
from os import environ
from mongoengine import connect
from pymongo.mongo_client import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure
from root.util.telegram import TelegramSender
from root.util.logger import Logger
import pymongo
from root.contants.messages import (DB_CONNECTION_ERROR, DB_CONNECTION_SUCCESS,
                                    DB_GENERIC_ERROR, GROUP_NOT_ALLOWED)
import requests
from datetime import datetime

logger = Logger()
sender = TelegramSender()

def format_date(date: datetime, show_year: bool = True) -> str:
    if show_year:
        return f"{date.day}/{date.month}/{date.year} {date.hour}:{date.minute}"
    else:
        return f'{date.day} {date.strftime("%b")} {date.hour}:{date.minute}'

def is_group_allowed(chat_id: int):
    groups = eval(retrieve_key("GROUP_ID"))
    if str(chat_id) in groups:
        return True
    else:
        TOKEN = retrieve_key("TOKEN")
        logger.warn(f"chat_id {chat_id} is not allowed")
        sender.send_message(TOKEN, chat_id, GROUP_NOT_ALLOWED)

def de_html(data):
    return sub("<.*?>|\n", "", str(data))

def generate_id():
    """[geenerate and id like 020120201801-7f36cd4a-6dfa-4b35-83c7-61d2ab8dafe0]

    Returns:
        [str]: [the id generated]
    """
    now = datetime.now()
    date = now.strftime("%m%d%Y%H%M")
    uuid = str(uuid4())
    return f"{date}-{uuid}"

def retrieve_key(key: str, decode=False):
    """[retrieve an environment variable]

    Args:
        key ([str]): [the key to retrieve]
        decode (bool, optional): [if the key should be base64 decoded]. Defaults to False.

    Returns:
        [string]: [the value or the environment variable]
    """
    try:
        data = environ[key]
        if decode:
            return sub('\n', '', b64decode(data).decode())
        return data
    except KeyError:
        logger.error("unable to find env variable {}".format(key))
        return None

def db_connect():
    """[connect to the desire database]"""
    USERNAME = retrieve_key('DBUSERNAME', False)
    PASSWORD = retrieve_key('DBPASSWORD', False)
    ADMIN = str(retrieve_key("TELEGRAM_BOT_ADMIN"))
    TOKEN = retrieve_key("TOKEN")
    HOST = retrieve_key('DBHOST', False)
    PORT = 27017
    DB = retrieve_key('DBNAME', False)
    CONNECTION = retrieve_key('CONNECTION', False)
    CONNECTION = CONNECTION.format(USERNAME, PASSWORD, HOST, DB)
    logger.info("connecting to db")
    try:
        client: MongoClient = connect(host=CONNECTION)
        #client = connect(DB, username=USERNAME, password=PASSWORD,
                         #host=HOST, port=PORT)
        client.server_info()
        logger.info(DB_CONNECTION_SUCCESS)
        sender.send_message(TOKEN, ADMIN, DB_CONNECTION_SUCCESS)
    except ServerSelectionTimeoutError:
        logger.error(DB_CONNECTION_ERROR)
        sender.send_message(TOKEN, ADMIN, DB_CONNECTION_ERROR)
    except OperationFailure:
        logger.error(DB_CONNECTION_ERROR)
        sender.send_message(TOKEN, ADMIN, DB_CONNECTION_ERROR)
    except Exception as e:
        logger.error(e)
        sender.send_message(TOKEN, ADMIN, DB_GENERIC_ERROR)

