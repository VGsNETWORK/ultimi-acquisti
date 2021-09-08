#!/usr/bin/env python3

""" Class of a CustomCategory mongoengine model """

from mongoengine import StringField, QuerySetManager, IntField
from root.model.base_model import BaseModel


class CustomCategory(BaseModel):
    """The class representing Custom Categories stored on the collection

    Args:
        BaseModel ([BaseModel]): extends the BaseModel class to get the generic document properties
    """

    objects = QuerySetManager()

    user_id = IntField(required=True)
    description = StringField(required=True)
