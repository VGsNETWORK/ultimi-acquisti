#!/usr/bin/env python3

from root.model.start_messages import StartMessages
from telegram.user import User
import telegram_utils.utils.logger as logger


def delete_start_message(user_id: int):
    logger.info(f"DELETING MESSAGE FOR USER {user_id}")
    try:
        StartMessages.objects.get(user_id=user_id).delete()
        logger.info(f"SUCCESFULLY DELETED MESSAGE FOR USER {user_id}")
    except Exception as e:
        logger.info(f"ERROR DELETING MESSAGE FOR USER {user_id}")
        logger.error(e)
        return


def update_or_create_start_message(user: User, message_id: int):
    StartMessages.objects(user_id=user.id).update_one(
        set__user_id=user.id,
        set__first_name=user.first_name,
        set__message_id=message_id,
        upsert=True,
    )


def get_start_messages():
    return StartMessages.objects()
