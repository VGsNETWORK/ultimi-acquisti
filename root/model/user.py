#!/usr/bin/env python3

from mongoengine import StringField, IntField, BooleanField
from root.model.base_model import BaseModel


class User(BaseModel):

    """[This class represent a user]
    @username = The telegram username
    @first_name = The telegram first name
    @last_name = The telegram last name
    @user_id = The telegram user id
    @rtb = The number of rtb (Rock The Ban) the user got
    @sed = How many sed commands the user sent
    """

    username = StringField()
    first_name = StringField()
    last_name = StringField()
    user_id = IntField(required=True, unique=True)
    is_admin = BooleanField(default=False)
