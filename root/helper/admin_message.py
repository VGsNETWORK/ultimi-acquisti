#!/usr/bin/env python3

from mongoengine.errors import DoesNotExist
from mongoengine.queryset.visitor import Q
from root.model import admin_message
from root.model.admin_message import AdminMessage
import telegram_utils.utils.logger as logger


def create_admin_message(message: str):
    AdminMessage(message=message).save()


def count_unread_admin_messages_for_user(user_id: int):
    messages = AdminMessage.objects.filter(Q(deleted__ne=user_id) & Q(read__ne=user_id))
    messages = list(messages)
    return len(messages)


def get_unread_admin_messages_for_user(user_id: int):
    return AdminMessage.objects.filter(Q(deleted__ne=user_id) & Q(read__ne=user_id))


def get_total_admin_messages(page_size: int = 5):
    total_products = AdminMessage.objects().count() / page_size
    if int(total_products) == 0:
        return 1
    elif int(total_products) < total_products:
        return int(total_products) + 1
    else:
        return int(total_products)


def purge_admin_message(communication_id: str):
    message: AdminMessage = find_admin_message_by_id(communication_id)
    if message:
        message.delete()


def get_total_unread_messages(user_id: int, page_size: int = 5):
    total_products = (
        AdminMessage.objects().filter(deleted__ne=user_id).count() / page_size
    )
    if int(total_products) == 0:
        return 1
    elif int(total_products) < total_products:
        return int(total_products) + 1
    else:
        return int(total_products)


def get_paged_admin_messages(page: int = 0, page_size: int = 5):
    return (
        AdminMessage.objects.order_by("-creation_date")
        .skip(page * page_size)
        .limit(page_size)
    )


def get_paged_unread_messages(user_id: int, page: int = 0, page_size: int = 5):
    return (
        AdminMessage.objects.filter(deleted__ne=user_id)
        .order_by("-creation_date")
        .skip(page * page_size)
        .limit(page_size)
    )


def find_admin_message_by_id(admin_message_id: str):
    try:
        return AdminMessage.objects.get(id=admin_message_id)
    except DoesNotExist:
        return None


def delete_admin_message(user_id: str, admin_message_id: str):
    logger.info("deleting admin_message for user %s" % user_id)
    message: AdminMessage = find_admin_message_by_id(admin_message_id)
    if message:
        logger.info("Found admin_message")
        deleted = list(message.deleted)
        if not user_id in deleted:
            logger.info(f"Adding user {user_id} to {admin_message_id}")
            deleted.append(user_id)
            message.deleted = deleted
            message.save()


def read_admin_message(user_id: str, admin_message_id: str):
    message: AdminMessage = find_admin_message_by_id(admin_message_id)
    if message:
        read = list(message.read)
        if not user_id in read:
            read.append(user_id)
            message.read = read
            message.save()
