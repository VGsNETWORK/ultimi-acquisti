#!/usr/bin/env python3

from mongoengine.errors import DoesNotExist
from root.model.wishlist import Wishlist


def find_wishlist_by_id(_id: str):
    try:
        wish: Wishlist = Wishlist.objects().get(id=_id)
        return wish
    except DoesNotExist:
        return


def remove_wishlist_item_for_user(_id: str):
    try:
        Wishlist.objects().get(id=_id).delete()
    except DoesNotExist:
        return


def delete_all_wishlist_for_user(user_id: int):
    try:
        for element in Wishlist.objects().filter(user_id=user_id):
            element.delete()
    except Exception:
        return


def delete_wishlist_photos(wish_id: str):
    wish: Wishlist = find_wishlist_by_id(wish_id)
    if wish:
        wish.photos = []
        wish.save()


def get_total_wishlist_pages_for_user(user_id: int, page_size: int = 5):
    total_products = Wishlist.objects().filter(user_id=user_id).count() / page_size
    if int(total_products) == 0:
        return 1
    elif int(total_products) < total_products:
        return int(total_products) + 1
    else:
        return int(total_products)


def find_wishlist_for_user(user_id: int, page: int = 0, page_size: int = 5):
    wish: Wishlist = (
        Wishlist.objects()
        .filter(user_id=user_id)
        .order_by("-creation_date")
        .skip(page * page_size)
        .limit(page_size)
    )
    return wish


def add_photo(_id: str, photo: str):
    wish: Wishlist = find_wishlist_by_id(_id)
    if wish:
        if len(wish.photos) < 10:
            wish.photos.insert(0, photo)
            wish.save()
        else:
            raise ValueError("max photo size reached")


def remove_photo(_id: str, photo: str):
    wish: Wishlist = find_wishlist_by_id(_id)
    if wish:
        wish.photos.remove(photo)
        wish.save()