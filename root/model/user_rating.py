#!/usr/bin/env python3


from mongoengine.fields import BooleanField, IntField, StringField
from root.model.base_model import BaseModel


class UserRating(BaseModel):
    approve_message_id = IntField(required=True)
    approve_chat_id = IntField(required=True)
    code = StringField(required=True)
    user_id = IntField(required=True)
    ux_vote = IntField(required=True)
    ux_comment = StringField()
    functionality_vote = IntField(required=True)
    functionality_comment = StringField()
    ui_vote = IntField(required=True)
    ui_comment = StringField()
    overall_vote = IntField(required=True)
    overall_comment = StringField()
    approved = BooleanField(default=False)