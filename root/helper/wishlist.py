#!/usr/bin/env python3

from mongoengine.errors import DoesNotExist
from root.model.wishlist import Wishlist


def remove_wishlist_item_for_user(_id: str):
    try:
        Wishlist.objects().get(id=_id).delete()
    except DoesNotExist:
        return


def get_total_wishlist_pages_for_user(user_id: int, page_size: int = 5):
    total_products = Wishlist.objects().filter(user_id=user_id).count() / page_size
    if int(total_products) == 0:
        return 1
    elif int(total_products) < total_products:
        return int(total_products) + 1
    else:
        return int(total_products)


def find_wishlist_for_user(user_id: int, page: int = 0, page_size: int = 5):
    return (
        Wishlist.objects()
        .filter(user_id=user_id)
        .order_by("-creation_date")
        .skip(page * page_size)
        .limit(page_size)
    )
