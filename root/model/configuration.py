#!/usr/bin/env python3

from mongoengine import StringField, QuerySetManager
from root.model.base_model import BaseModel


class Configuration(BaseModel):

    objects = QuerySetManager()

    code = StringField(required=True, unique=True)
    value = StringField(required=True)
