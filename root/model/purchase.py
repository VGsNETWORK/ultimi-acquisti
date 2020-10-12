#!/usr/bin/env python3

from mongoengine import IntField, FloatField
from root.model.base_model import BaseModel


class Purchase(BaseModel):

    """[This class represent a Purchage]
    @price = the price spent
    @user_id = The telegram user id
    """

    user_id = IntField()
    price = FloatField()
    message_id = IntField(unique=True)
    chat_id = IntField()