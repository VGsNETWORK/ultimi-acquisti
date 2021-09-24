#!/usr/bin/env python3

from mongoengine.fields import IntField
from root.model.base_model import BaseModel


class Whitelist(BaseModel):
    telegram_id = IntField(required=True)