#!/usr/bin/env python3

from root.model.user import User
from mongoengine.errors import DoesNotExist
from telegram import User as TelegramUser

def user_exists(user_id: int) -> bool:
    try:
        User.objects.get(user_id=user_id)
        return True
    except DoesNotExist:
        return False

def is_admin(user_id: int) -> bool:
    if (user_exists(user_id)):
        user: User = retrieve_user(user_id)
        return user.is_admin
    return False

def create_user(user: TelegramUser) -> None:
    User(username=user.username, user_id=user.id,
         first_name=user.first_name, last_name=user.last_name).save()

def retrieve_user(user_id: int) -> User:
    try:
        return User.objects.get(user_id=user_id)
    except DoesNotExist:
        return None

def retrieve_admins() -> [User]:
    return User.objects.filter(is_admin=True)
