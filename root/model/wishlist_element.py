#!/usr/bin/env python3

from mongoengine.fields import IntField, ListField, StringField
from telegram_utils.model.base_model import BaseModel


class WishlistElement(BaseModel):
    user_id = IntField()
    wishlist_id = StringField()
    description = StringField()
    quantity = IntField()
    links = ListField(StringField())
    category = StringField()
    photos = ListField(StringField())