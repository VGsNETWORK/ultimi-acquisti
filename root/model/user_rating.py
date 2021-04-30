#!/usr/bin/env python3


from mongoengine.fields import BooleanField, IntField, StringField
from root.model.base_model import BaseModel


class UserRating(BaseModel):
    ui_vote = IntField(required=True)
    ui_comment = StringField()
    functionality_vote = IntField(required=True)
    functionality_comment = StringField()
    ux_vote = IntField(required=True)
    ux_comment = StringField()
    general_vote = IntField(required=True)
    general_comment = StringField()
    approved = BooleanField(default=False)