#!/usr/bin/env python3

from mongoengine.errors import DoesNotExist
from root.model.custom_category import CustomCategory


def find_category_for_user_by_description(user_id: int, description: str):
    try:
        return CustomCategory.objects().get(user_id=user_id, description=description)
    except DoesNotExist:
        return None


def find_category_for_user_by_id(user_id: int, _id: str):
    try:
        return CustomCategory.objects().get(user_id=user_id, id=_id)
    except DoesNotExist:
        return None


def delete_category_for_user(user_id: int, description: str):
    category: CustomCategory = find_category_for_user_by_description(
        user_id, description
    )
    if category:
        category.delete()


def create_category_for_user(user_id: int, description: str):
    return CustomCategory(user_id=user_id, description=description).save()


def find_categories_for_user(user_id: int):
    return CustomCategory.objects().filter(user_id=user_id)


def count_categories_for_user(user_id: int):
    return len(CustomCategory.objects().filter(user_id=user_id))