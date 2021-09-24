#!/usr/bin/env python3

from mongoengine.errors import DoesNotExist
from root.model.whitelist import Whitelist


def whitelist_chat(chat_id: int):
    Whitelist(telegram_id=chat_id).save()


def is_whitelisted(chat_id: int):
    try:
        return Whitelist.objects().get(telegram_id=chat_id)
    except DoesNotExist:
        return False
