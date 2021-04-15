#!/usr/bin/env python3

""" File to handle messages to delete and who owns them """

from os import environ
import redis
import root.util.logger as logger


def is_develop() -> bool:
    """Chek if the profile is set to develop

    Returns:
        bool: If the profile is set to develop
    """
    try:
        profile = environ["PROFILE"]
        return profile == "develop"
    except KeyError:
        return False


MESSAGE_PREFIX = "ultimi_acquisti"
db_index: int = 15 if is_develop() else 1
red = redis.Redis(db=db_index)


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
        raise ValueError(f"session ended for the message {message_id}...")


def delete_message(message_id: int) -> None:
    """Deletes a message from redis

    Args:
        message_id (int): The message to delete
    """
    message_key = f"{MESSAGE_PREFIX}_{message_id}"
    red.delete(message_key)


def add_message(message_id: int, user_id: int, add: bool = True) -> None:
    """Store a message in redis

    Args:
        message_id (int): The message_id of the message
        user_id (int): The user who typed the command
        add (bool): if True, add + 1 to the message_id
    """
    if add:
        message_id += 1
    logger.info(f"Creating redis message for {message_id} - {user_id}")
    message_key = f"{MESSAGE_PREFIX}_{message_id}"
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
