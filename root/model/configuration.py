#!/usr/bin/env python3

""" Class of a Configuration mongoengine model """

from mongoengine import StringField, QuerySetManager
from root.model.base_model import BaseModel


class Configuration(BaseModel):
    """The class representing configurations stored on the collection

    Args:
        BaseModel ([BaseModel]): extends the BaseModel class to get the generic document properties
    """

    objects = QuerySetManager()

    code = StringField(required=True, unique=True)
    value = StringField(required=True)
