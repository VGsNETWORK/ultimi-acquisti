#!/usr/bin/env python3

""" Class of a Purchase mongoengine model """

from mongoengine import IntField, FloatField
from root.model.base_model import BaseModel


class Purchase(BaseModel):
    """The class representing purchases stored on the collection

    Args:
        BaseModel ([BaseModel]): extends the BaseModel class to get the generic document properties
    """

    user_id = IntField()
    price = FloatField()
    message_id = IntField(unique=True)
    chat_id = IntField()
