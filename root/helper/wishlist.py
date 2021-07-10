#!/usr/bin/env python3

from typing import List

import telegram_utils.utils.logger as logger
from mongoengine.errors import DoesNotExist
from pymongo.command_cursor import CommandCursor
from root.helper.user_helper import change_wishlist
from root.model import user, wishlist
from root.model.wishlist import Wishlist
from root.model.wishlist_element import WishlistElement


def find_wishlist_by_id(_id: str):
    try:
        wish: Wishlist = Wishlist.objects().get(id=_id)
        return wish
    except DoesNotExist:
        return


def create_wishlist(description: str, title: str, user_id: int):
    Wishlist(description=description, title=title, user_id=user_id).save()


def create_wishlist_if_empty(user_id: int):
    logger.info("creating wishlist")
    try:
        wishlists = Wishlist.objects().filter(user_id=user_id)
        if len(wishlists) == 0:
            logger.info("CREATING WISHLIST FOR USER %s" % user_id)
            wish = Wishlist(
                title="La mia Lista",
                user_id=user_id,
                description="",
                default_wishlist=True,
            ).save()
            change_wishlist(user_id, str(wish.id))
            assign_all_wishlist_elements(user_id, str(wish.id))
            return True
        return False
    except Exception as e:
        return False


def assign_all_wishlist_elements(user_id: int, wishlist_id: str):
    elements: List[WishlistElement] = WishlistElement.objects().filter(user_id=user_id)
    logger.info("CHANGING %s with [%s] for %s" % (len(elements), wishlist_id, user_id))
    for element in elements:
        logger.info("OLD [%s] - NEW [%s]" % (wishlist_id, element.wishlist_id))
        element.wishlist_id = wishlist_id
        logger.info("OLD [%s] - NEW [%s]" % (wishlist_id, element.wishlist_id))
        element.save()


def find_default_wishlist(user_id: int):
    try:
        return Wishlist.objects().get(user_id=user_id, default_wishlist=True)
    except DoesNotExist:
        return None


def remove_wishlist_for_user(_id: str, user_id: int):
    try:
        wish: Wishlist = Wishlist.objects().get(id=_id)
        if not wish.default_wishlist:
            wish.delete()
    except DoesNotExist:
        return


def count_all_wishlists_for_user(user_id: int):
    return len(Wishlist.objects().filter(user_id=user_id))


def get_total_wishlist_pages_for_user(user_id: int, page_size: int = 5):
    total_products = Wishlist.objects().filter(user_id=user_id).count() / page_size
    if int(total_products) == 0:
        return 1
    elif int(total_products) < total_products:
        return int(total_products) + 1
    else:
        return int(total_products)


def find_wishlist_for_user(
    user_id: int, page: int = 0, page_size: int = 5, default_wishlist: bool = False
):
    wish: Wishlist = (
        Wishlist.objects()
        .filter(user_id=user_id, default_wishlist=default_wishlist)
        .order_by("-creation_date")
        .skip(page * page_size)
        .limit(page_size)
    )
    return wish
