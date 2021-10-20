#!/usr/bin/env python3


from mongoengine.fields import (
    BooleanField,
    DateTimeField,
    FloatField,
    IntField,
    ListField,
    StringField,
)
from root.model.base_model import BaseModel


class TrackedLink(BaseModel):
    title = StringField()
    link = StringField(required=True)
    price = FloatField(reqquired=True)
    platform = StringField(required=True)
    store = StringField(required=True)
    base_url = StringField(required=True)
    code = StringField(required=True, unique=True)
    subscribers = ListField(IntField())
    collect_available = BooleanField()
    delivery_available = BooleanField()
    bookable = BooleanField()
    sold_out = BooleanField()
    digital = BooleanField()
    deals_end = DateTimeField()
    deals_percentage = FloatField()
    included_in_premium = BooleanField()
    premium_type = StringField()