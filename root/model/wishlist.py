#!/usr/bin/env python3

from mongoengine.fields import IntField, StringField
from telegram_utils.model.base_model import BaseModel


class Wishlist(BaseModel):
    user_id = IntField()
    description = StringField()
    quantity = IntField()
    link = StringField()