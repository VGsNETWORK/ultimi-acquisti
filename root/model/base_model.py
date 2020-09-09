#!/usr/bin/env python3

from mongoengine import Document, DateTimeField
from datetime import datetime


class BaseModel(Document):

    """ This is the Base Model, it contains some common information
        that all documents should have """

    meta = {"allow_inheritance": True, "abstract": True}
    creation_date = DateTimeField(default=datetime.now)
