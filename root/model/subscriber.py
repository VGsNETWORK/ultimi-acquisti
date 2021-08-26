#!/usr/bin/env python3

# region
from mongoengine.fields import BooleanField, FloatField, IntField, StringField
from telegram_utils.model.base_model import BaseModel

# endregion


class Subscriber(BaseModel):

    meta = {"allow_inheritance": True}
    user_id = IntField(required=True)
    product_code = StringField(required=True)
    lowest_price = FloatField(required=True)
    never_updated = BooleanField(required=True)