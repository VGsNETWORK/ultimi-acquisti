#!/usr/bin/env python3

from mongoengine.errors import DoesNotExist
from mongoengine.queryset.visitor import Q
from root.model.admin_message import AdminMessage


def count_unread_admin_messages_for_user(user_id: int):
    messages = AdminMessage.objects.filter(Q(read__ne=user_id))
    messages = list(messages)
    return len(messages)


def get_unread_admin_messages_for_user(user_id: int):
    return AdminMessage.objects.filter(Q(read__ne=user_id))


def find_admin_message_by_id(admin_message_id: str):
    try:
        return AdminMessage.objects.get(id=admin_message_id)
    except DoesNotExist:
        return None


def read_admin_message(user_id: str, admin_message_id: str):
    message: AdminMessage = find_admin_message_by_id(admin_message_id)
    if message:
        read = list(message.read)
        if not user_id in read:
            read.append(user_id)
            message.read = read
            message.save()
