#!/usr/bin/env python3

from root.helper.redis_message import is_develop
from typing import List

import telegram_utils.utils.logger as logger
from mongoengine.errors import DoesNotExist
from pymongo.command_cursor import CommandCursor
from telegram_utils.utils.tutils import log
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


def find_wishlist_by_for_index(index: int, user_id: int):
    try:
        wish: Wishlist = Wishlist.objects().get(index=index, user_id=user_id)
        return wish
    except DoesNotExist:
        return


def get_last_wishlist_index(user_id: int):
    wishlists: List[Wishlist] = find_wishlist_for_user(user_id)
    wishlists = list(wishlists)
    if wishlists:
        return max([wishlist.index for wishlist in wishlists])
    else:
        return 0


def create_wishlist(description: str, title: str, user_id: int):
    index = get_last_wishlist_index(user_id)
    Wishlist(
        description=description, title=title, user_id=user_id, index=index + 1
    ).save()


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
                index=0,
            ).save()
            change_wishlist(user_id, str(wish.id))
            assign_all_wishlist_elements(user_id, str(wish.id))
            return True
        else:
            for index, wishlist in enumerate(list(wishlists)):
                if not wishlist.index:
                    wishlist.index = index
                    wishlist.save()
            logger.info("WISHLIST BIGGER THAN 0")
        return False
    except Exception as e:
        logger.error(e)
        return False


def assign_all_wishlist_elements(user_id: int, wishlist_id: str):
    elements: List[WishlistElement] = WishlistElement.objects().filter(user_id=user_id)
    logger.info("CHANGING %s with [%s] for %s" % (len(elements), wishlist_id, user_id))
    for element in elements:
        element.wishlist_id = wishlist_id
        element.save()


def find_default_wishlist(user_id: int):
    try:
        return Wishlist.objects().get(user_id=user_id, default_wishlist=True)
    except DoesNotExist:
        return None


def find_wishlist_with_index_bigger_than(index: int, user_id: int):
    wishlists: List[Wishlist] = Wishlist.objects().filter(
        user_id=user_id, index__gte=index
    )
    wishlists = list(wishlists)
    wishlists.sort(key=lambda x: x.index, reverse=False)
    return wishlists


def remove_wishlist_for_user(_id: str, user_id: int):
    try:
        wish: Wishlist = Wishlist.objects().get(id=_id)
        if not wish.default_wishlist:
            index = wish.index
            wishlists: List[Wishlist] = find_wishlist_with_index_bigger_than(
                index, user_id
            )
            for wishlist in wishlists:
                wishlist.index -= 1
                wishlist.save()
            wish.delete()
            if is_develop():
                message = f"USER_ID: {user_id}\n"
                wishlists = find_wishlist_for_user(user_id)
                wishlists = list(wishlists)
                wishlists.sort(key=lambda x: x.index, reverse=True)
                message += "\n".join(
                    [
                        f"    —  <b>{wishlist.title}</b>: <i>{wishlist.index}</i>"
                        for wishlist in wishlists
                    ]
                )
                log(0, message, disable_notification=True)
    except DoesNotExist as e:
        logger.error(e)
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


def find_wishlist_not_id(wishlist_id: str, user_id: int):
    return (
        Wishlist.objects()
        .filter(id__ne=wishlist_id, user_id=user_id)
        .order_by("-index")
    )


def change_wishlist_title(wishlist_id: str, title: str):
    wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
    if wishlist:
        wishlist.title = title
        wishlist.save()


def find_wishlist_for_user(
    user_id: int, page: int = 0, page_size: int = 10, default_wishlist: bool = False
):
    logger.info(f"page: {page} - page_size: {page_size} - default: {default_wishlist}")
    wish: Wishlist = (
        Wishlist.objects()
        .filter(user_id=user_id, default_wishlist=default_wishlist)
        .order_by("-index")
        .skip(page * page_size)
        .limit(page_size)
    )
    return wish
