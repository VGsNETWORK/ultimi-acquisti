#!/usr/bin/env python3

""" File used to manage the bot configurations """

from root.model.notification import Notification
import telegram_utils.utils.logger as logger


def create_notification(user_id: int, message: str, category: str = ""):
    Notification(user_id=user_id, message=message, category=category, read=False).save()


def find_notifications_for_user(
    user_id: int,
    page: int = 0,
    page_size: int = 100,
):
    logger.info(f"page: {page} - page_size: {page_size}")
    notifications: Notification = (
        Notification.objects()
        .filter(user_id=user_id)
        .order_by("-creation_date")
        .skip(page * page_size)
        .limit(page_size)
    )
    return notifications


def count_unread_notifications(
    user_id: int,
):
    return len(Notification.objects().filter(user_id=user_id))


def mark_all_notification_as_read(
    user_id: int,
):
    Notification.objects().filter(user_id=user_id).update(set__read=True)
