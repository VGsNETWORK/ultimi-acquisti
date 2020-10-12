#!/usr/bin/env python3

from root.model.base_model import BaseModel
from mongoengine import StringField


class Configuration(BaseModel):
    code = StringField(required=True, unique=True)
    value = StringField(required=True)
