#!/usr/bin/env python3

""" Class of a Base mongoengine model """

from datetime import datetime
from mongoengine import Document, DateTimeField, QuerySetManager


class BaseModel(Document):
    """This is the Base Model, it contains some common information that all documents should have

    Args:
        Document ([Document]): extends the document class to get the mongoegine functions
    """

    objects = QuerySetManager()
    meta = {"allow_inheritance": True, "abstract": True}
    creation_date = DateTimeField(default=datetime.now)
