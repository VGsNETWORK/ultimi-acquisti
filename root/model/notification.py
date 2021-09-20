#!/usr/bin/env python3

""" Class of a Notification mongoengine model """

from mongoengine import StringField, IntField, BooleanField
from root.model.base_model import BaseModel


class Notification(BaseModel):
    """The class representing notifications stored on the collection

    Args:
        BaseModel ([BaseModel]): extends the BaseModel class to get the generic document properties
    """

    message = StringField(required=True)
    user_id = IntField(required=True)
    category = StringField(required=True)
    read = BooleanField(required=True)
