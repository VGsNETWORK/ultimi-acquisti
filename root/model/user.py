#!/usr/bin/env python3

""" Class of a User mongoengine model """

from mongoengine import StringField, IntField, BooleanField
from root.model.base_model import BaseModel


class User(BaseModel):
    """The class representing users stored on the collection

    Args:
        BaseModel ([BaseModel]): extends the BaseModel class to get the generic document properties
    """

    username = StringField()
    first_name = StringField()
    last_name = StringField()
    user_id = IntField(required=True, unique=True)
    is_admin = BooleanField(default=False)
    show_purchase_tips = BooleanField(default=True)
