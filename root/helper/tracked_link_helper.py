#!/usr/bin/env python3

from root.helper.subscriber_helper import remove_subscriber
from mongoengine.errors import DoesNotExist
from root.model.tracked_link import TrackedLink
import telegram_utils.utils.logger as logger

def find_link_by_code(code: str):
    try:
        return TrackedLink.objects().get(code=code)
    except DoesNotExist:
        return None

def find_link_by_link(link: str):
    try:
        return TrackedLink.objects().get(link=link)
    except DoesNotExist:
        return None

def find_link_by_id(id: str):
    try:
        return TrackedLink.objects().get(id=id)
    except DoesNotExist:
        return None

def get_total_pages(page_size: int = 5):
    total_products = TrackedLink.objects().count() / page_size
    if int(total_products) == 0:
        return 1
    elif int(total_products) < total_products:
        return int(total_products) + 1
    else:
        return int(total_products)

def get_paged_link(page: int = 0, page_size: int = 5):
    return TrackedLink.objects().skip(page * page_size).limit(page_size)

def get_paged_link_for_user(user_id: int, page: int = 0, page_size: int = 5):
    return TrackedLink.objects().filter(subscribers__contains=user_id).skip(page * page_size).limit(page_size)

def update_or_create_scraped_link(product: dict):
    """Create a new product from string"""
    # fmt: off
    # check if the data is empty
    code = product["code"]
    if not code or not product:
        return False
    # create a temporary product Object
    tracked: TrackedLink = TrackedLink(**product, subscribers=[])
    if tracked.link:
        # format picture and price
        # update the document if present or create a new one
        TrackedLink.objects(code=code).update_one(set__code=code,
                                              set__price=product["price"],
                                              set__platform=product["platform"],
                                              set__store=product["store"],
                                              set__base_url=product["base_url"],
                                              set__link=product["link"],
                                              set__collect_available=product["collect_available"],
                                              set__delivery_available=product["delivery_available"],
                                              upsert=True)
        return True
        # fmt: on
    return False

def add_subscriber_to_link(code: str, user_id=int):
    try:
        tracked: TrackedLink = TrackedLink.objects().get(code=code)
        if not user_id in tracked.subscribers:
            tracked.subscribers.append(user_id)
            # update_subscriber(user_id, code, tracked.price)
            tracked.save()
    except DoesNotExist:
        return


def remove_tracked_subscriber(code: str, user_id: int):
    try:
        tracked_link: TrackedLink = TrackedLink.objects().get(code=code)
        if user_id in tracked_link.subscribers:
            tracked_link.subscribers.remove(user_id)
            remove_subscriber(user_id, tracked_link.code)
            tracked_link.save()
            if len(tracked_link.subscribers) == 0:
                logger.info("removed tracked link for link [%s]" % code)
                tracked_link.delete()
            logger.info("removed subscriber for link [%s]" % code)
    except DoesNotExist:
        return