#!/usr/bin/env python3

from mongoengine.fields import BooleanField, IntField, ListField, StringField
from telegram_utils.model.base_model import BaseModel


class Wishlist(BaseModel):
    user_id = IntField()
    title = StringField()
    description = StringField()
    default_wishlist = BooleanField(default=False)
    index = IntField()