#!/usr/bin/env python3

# region
from mongoengine.errors import DoesNotExist
from root.model.subscriber import Subscriber
import telegram_utils.utils.logger as logger

# endregion


def update_subscriber(user_id: str, product_code: str, price: float):
    Subscriber.objects(user_id=user_id, product_code=product_code).update_one(
        set__product_code=product_code,
        set__user_id=user_id,
        set__lowest_price=price,
        upsert=True,
    )


def find_subscriber(user_id: int, product_code: str):
    try:
        return Subscriber.objects.get(user_id=user_id, product_code=product_code)
    except DoesNotExist:
        return None


def remove_subscriber(user_id: int, product_code: str):
    try:
        Subscriber.objects.get(user_id=user_id, product_code=product_code).delete()
    except DoesNotExist:
        logger.error(
            "Unable to find subscriber to remove with user_id: %s and code: %s"
            % (user_id, product_code)
        )
        return