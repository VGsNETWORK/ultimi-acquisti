#!/usr/bin/env python3

from mongoengine.errors import DoesNotExist
from root.model.wishlist_element import WishlistElement


def find_wishlist_element_by_id(_id: str):
    try:
        wish: WishlistElement = WishlistElement.objects().get(id=_id)
        wish.photos.reverse()
        return wish
    except DoesNotExist:
        return


def remove_wishlist_element_item_for_user(_id: str):
    try:
        WishlistElement.objects().get(id=_id).delete()
    except DoesNotExist:
        return


def get_total_wishlist_element_pages_for_user(user_id: int, page_size: int = 5):
    total_products = (
        WishlistElement.objects().filter(user_id=user_id).count() / page_size
    )
    if int(total_products) == 0:
        return 1
    elif int(total_products) < total_products:
        return int(total_products) + 1
    else:
        return int(total_products)


def find_wishlist_element_for_user(user_id: int, page: int = 0, page_size: int = 5):

    wish: WishlistElement = (
        WishlistElement.objects()
        .filter(user_id=user_id)
        .order_by("-creation_date")
        .skip(page * page_size)
        .limit(page_size)
    )
    wish.photos.reverse()
    return wish
