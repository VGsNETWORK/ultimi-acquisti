#!/usr/bin/env python3

""" File with various functions to help handle users """

from typing import List
from telegram import User as TelegramUser
from mongoengine.errors import DoesNotExist
from root.model.user import User
import telegram_utils.utils.logger as logger
from root.helper.wishlist import find_default_wishlist


def get_current_wishlist_id(user_id: int):
    user: User = retrieve_user(user_id)
    if user:
        wishlist = user.current_wishlist
        if wishlist:
            return wishlist
        else:
            def_wishlist = find_default_wishlist(user_id)
            if def_wishlist:
                user.current_wishlist = str(def_wishlist.id)
                user.save()
                return str(def_wishlist.id)
    return None


def change_wishlist(user_id: int, wishlist_id: str):
    user: User = retrieve_user(user_id)
    if user:
        logger.info(
            "changing default wishlist for user %s with [%s]"
            % (user.user_id, wishlist_id)
        )
        user.current_wishlist = str(wishlist_id)
        user.save()


def user_exists(user_id: int) -> bool:
    """Check if the user exists in the database

    Args:
        user_id (int): The user_id of the user to check

    Returns:
        bool: If the user exists
    """
    try:
        User.objects.get(user_id=user_id)
        return True
    except DoesNotExist:
        return False


def is_admin(user_id: int) -> bool:
    """Check if the user is an admin of the bot

    Args:
        user_id (int): The user_id of the user to check

    Returns:
        bool: If the user is an admin
    """
    if user_exists(user_id):
        user: User = retrieve_user(user_id)
        return user.is_admin
    return False


def create_user(user: TelegramUser) -> None:
    """Create a user from a telegram user object

    Args:
        user (User): The telegram user Object
    """
    User(
        username=user.username,
        user_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
    ).save()


def retrieve_user(user_id: int) -> User:
    """Get a user

    Args:
        user_id (int): The user_id to indentify the user

    Returns:
        User: The user matching the query
    """
    try:
        return User.objects.get(user_id=user_id)
    except DoesNotExist:
        return None


def retrieve_admins() -> List[User]:
    """Get all admins of the bot

    Returns:
        [User]: List of admins
    """
    return User.objects.filter(is_admin=True)
