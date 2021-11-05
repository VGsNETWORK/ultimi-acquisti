#!usr/bin/env python3

from mongoengine.fields import IntField, StringField
from root.model.base_model import BaseModel


class StartMessages(BaseModel):
    first_name = StringField()
    user_id = IntField()
    message_id = IntField()