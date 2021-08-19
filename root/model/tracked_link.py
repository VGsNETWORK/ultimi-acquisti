#!/usr/bin/env python3


from mongoengine.fields import (
    BooleanField,
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