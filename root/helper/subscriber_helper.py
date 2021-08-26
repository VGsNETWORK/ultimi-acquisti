#!/usr/bin/env python3

# region
from mongoengine.errors import DoesNotExist
from root.model.subscriber import Subscriber
import telegram_utils.utils.logger as logger

# endregion


def update_subscriber(
    user_id: str, product_code: str, price: float, reset_used: bool = False
):
    subscriber: Subscriber = find_subscriber(user_id, product_code)
    if subscriber:
        logger.info("Using existing subscriber")
        subscriber.lowest_price = price
        if reset_used:
            if subscriber.never_updated:
                subscriber.never_updated = False
    else:
        logger.info("creating a new one")
        create_subscriber(user_id, product_code, price)


def create_subscriber(user_id: str, product_code: str, price: float):
    Subscriber(
        user_id=user_id,
        product_code=product_code,
        lowest_price=price,
        never_updated=True,
    ).save()


def find_subscriber(user_id: int, product_code: str):
    try:
        logger.info("finding for %s - %s" % (user_id, product_code))
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