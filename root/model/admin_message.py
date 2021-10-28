#!/usr/bin/env python3

""" Class of a Notification mongoengine model """

from mongoengine import StringField, IntField, BooleanField
from mongoengine.fields import ListField
from root.model.base_model import BaseModel


class AdminMessage(BaseModel):
    """The class representing notifications stored on the collection

    Args:
        BaseModel ([BaseModel]): extends the BaseModel class to get the generic document properties
    """

    message = StringField(required=True)
    read = ListField(IntField())
    deleted = ListField(IntField())
