#!/usr/bin/env python3

""" File to handle messages to delete and who owns them """

import redis
from root.util.logger import Logger

MESSAGE_PREFIX = "ultimi_acquisti"
red = redis.Redis(db=1)
logger = Logger()


def is_owner(message_id: int, user_id: int) -> bool:
    """Check if a message is owned by the user who's interacting with it

    Args:
        message_id (int): The message_id stored in the key
        user_id (int): The user who owns the message

    Returns:
        bool: If it's the owner
    """
    message_key = f"{MESSAGE_PREFIX}_{message_id}"
    value = red.get(message_key)
    if value:
        return value.decode() == str(user_id)
    else:
        logger.error(f"** REDIS: {message_key} does not belong to anyone")
        raise ValueError("session ended for the message...")


def delete_message(message_id: int) -> None:
    """Deletes a message from redis

    Args:
        message_id (int): The message to delete
    """
    message_key = f"{MESSAGE_PREFIX}_{message_id}"
    red.delete(message_key)


def add_message(message_id: int, user_id: int) -> None:
    """Store a message in redis

    Args:
        message_id (int): The message_id of the message
        user_id (int): The user who typed the command
    """
    message_key = f"{MESSAGE_PREFIX}_{message_id + 1}"
    red.set(message_key, user_id)


def message_exist(message_id: int) -> str:
    """Check if a message is stored in redis

    Args:
        message_id (int): The message_id to check

    Returns:
        str: the result of the query
    """
    message_key = f"{MESSAGE_PREFIX}_{message_id}"
    return red.get(message_key)


def reset_redis():
    """Deletes all entry in redis db"""
    red.flushdb()
