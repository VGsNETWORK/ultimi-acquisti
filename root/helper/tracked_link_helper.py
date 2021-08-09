#!/usr/bin/env python3

from root.helper.subscriber_helper import remove_subscriber
from mongoengine.errors import DoesNotExist
from root.model.tracked_link import TrackedLink


def find_link_by_code(code: str):
    try:
        return TrackedLink.objects().get(code=code)
    except DoesNotExist:
        return None


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
                tracked_link.delete()
    except DoesNotExist:
        return