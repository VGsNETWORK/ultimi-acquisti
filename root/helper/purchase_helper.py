#!/usr/bin/env python3

""" File with various functions to help handle purchases """

import re
from datetime import datetime
from calendar import monthrange
from mongoengine.errors import DoesNotExist
import root.util.logger as logger
from root.model.purchase import Purchase


def before(to_check: str, to_check_with: str, to_check_from: str) -> bool:
    """Check if a string is before another

    Args:
        to_check (str): The string to check
        to_check_with (str): The string to check with
        to_check_from (str): The string to check from

    Returns:
        bool: if the to_check is before
    """
    open_parens = 0
    for char in to_check_from:
        if char == to_check:
            open_parens += 1
        elif char == to_check_with:
            open_parens -= 1
            if open_parens < 0:
                return False
    return open_parens == 0


def convert_to_float(price: str) -> float:
    """Convert a string number into a valid float

    Args:
        price (str): The string price to convert into a float

    Returns:
       float : The price converted into a float
    """
    logger.info(f"converting {price}")
    dots = re.findall("\\.", price)
    commas = re.findall("\\,", price)
    apostrophes = re.findall("'", price)
    if len(commas) == 1 and len(dots) == 1:
        if before(",", ".", price):
            price = price.replace(",", "")
        else:
            price = price.replace(".", "").replace(",", ".")
    elif len(commas) == 1 and len(apostrophes) == 1:
        price = price.replace("'", "").replace(",", ".")
    elif len(apostrophes) == 1:
        price = price.replace("'", "")
    elif len(commas) == 2:
        price = price.replace(",", "", 1).replace(",", ".")
    elif len(dots) == 2:
        price = price.replace(".", "", 1)
    elif len(commas) == 1:
        if len(price.split(",")[1]) > 2:
            price = price.replace(",", "")
        else:
            price = price.replace(",", ".")
    elif len(dots) == 1:
        if len(price.split(".")[1]) > 2:
            price = price.replace(".", "")
    return float(price)


def create_purchase(
    user_id: int,
    price: float,
    message_id: int,
    chat_id: int,
    creation_date: datetime = None,
    description: str = "",
) -> None:
    """Store a new purchase from a user in the database or modify an existing one

    Args:
        user_id (int): The user_id of who purchase the item
        price (float): The price of the item
        message_id (int): The Telegram message_if of the purchase
        chat_id (int): The chat where the purchase was posted
        creation_date (datetime, optional): When the post was created. Defaults to None.
        description (str, optional): The description of the purchase. Defaults to ''.
    """
    try:
        Purchase.objects().get(message_id=message_id)
        logger.info(f"try to modifying purchase {message_id}")
        Purchase.objects(message_id=message_id).update(
            set__price=price,
            set__creation_date=creation_date,
            set__description=description,
        )
        return
    except DoesNotExist:
        pass
    if creation_date:
        Purchase(
            user_id=user_id,
            price=price,
            message_id=message_id,
            chat_id=chat_id,
            creation_date=creation_date,
            description=description,
        ).save()
    else:
        Purchase(
            user_id=user_id,
            price=price,
            message_id=message_id,
            chat_id=chat_id,
            description=description,
        ).save()


def find_by_message_id_and_chat_id(message_id: int, chat_id: int) -> Purchase:
    """Find a purchase using the message_id

    Args:
        message_id (int): The message_id to find

    Returns:
        Purchase: The purchase if found
    """
    try:
        return Purchase.objects.get(message_id=message_id, chat_id=chat_id)
    except DoesNotExist:
        return None


def find_by_message_id(message_id: int) -> Purchase:
    """Find a purchase using the message_id

    Args:
        message_id (int): The message_id to find

    Returns:
        Purchase: The purchase if found
    """
    return Purchase.objects.get(message_id=message_id)


def retrive_purchases_for_user(user_id: int):
    """retrieve all purchases for a user

    Args:
        user_id (int): The user_id to use for the query

    Returns:
        [Purchase]: List of purchases
    """
    try:
        return Purchase.objects.filter(user_id=user_id)
    except DoesNotExist:
        return None


def retrieve_month_purchases_for_user(
    user_id: int, month: int = None, year: int = None
):
    """Retrieve all purchases in a month

    Args:
        user_id (int): The user_id to use for the query
        month (int, optional): month to query. Defaults to None.
        year (int, optional): year to query. Defaults to None.

    Returns:
        [Purchase]: List of purchases
    """
    try:
        month = 12 if month < 1 else month
        month = 1 if month > 12 else month
        current_date = datetime.now()
        month = month if month else current_date.month
        year = year if year else current_date.year
        _, end = monthrange(year, month)
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, end, 23, 59, 59, 59)
        return Purchase.objects.filter(
            user_id=user_id, creation_date__lte=end_date, creation_date__gte=start_date
        ).order_by("creation_date")
    except DoesNotExist:
        return None


def delete_purchase(user_id: int, message_id: int) -> None:
    """Delete a purchase a user made

    Args:
        user_id (int): The user who purchase the item
        message_id (int): The purchase to delete
    """
    logger.info(f"finding purchase {message_id} for user {user_id}")
    Purchase.objects.filter(user_id=user_id).get(message_id=message_id).delete()


def delete_purchase_forced(message_id: int, chat_id: int) -> None:
    """Delete a purchase

    Args:
        message_id (int): The purchase to delete
    """
    logger.info(f"finding purchase {message_id}")
    Purchase.objects.get(message_id=message_id, chat_id=chat_id).delete()


def retrieve_sum_for_user(user_id: int) -> float:
    """Return how much the user has spent up until now

    Args:
        user_id (int): The user_id to use for the query

    Returns:
        float: How much the user has spent up until now
    """
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$user_id", "total": {"$sum": "$price"}}},
    ]
    res = list(Purchase.objects.aggregate(*pipeline))
    return 0.0 if len(res) == 0 else res[0]["total"]


def retrieve_sum_for_current_month(user_id: int) -> float:
    """How much the user has spent in this month

    Args:
        user_id (int): The user_id to use for the query

    Returns:
        float: How much the user has spent int this month
    """
    month = datetime.now().month
    return retrieve_sum_for_month(user_id, month)


def retrieve_sum_for_month(
    user_id: int, month: int, year: int = None, negative: bool = False
) -> float:
    """How much the user has spent in a specific month and year

    Args:
        user_id (int): The user_id to use for the query
        month (int): The month to query
        year (int, optional): The year to query. Defaults to None.

    Returns:
        float: [description]
    """
    month = 12 if month < 1 else month
    month = 1 if month > 13 else month
    current_date = datetime.now()
    year = year if year else current_date.year
    _, end = monthrange(year, month)
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month, end, 23, 59, 59, 59)
    return retrieve_sum_between_date(user_id, start_date, end_date, negative)


def retrieve_sum_for_current_year(user_id: int) -> float:
    """How much the user has spent in this year

    Args:
        user_id (int): The user_id to use for the query

    Returns:
        float: How much the user has spent in a this year
    """
    return retrieve_sum_for_year(user_id, datetime.now().year)


def retrieve_sum_for_year(user_id: int, year: int) -> float:
    """How much the user has spent in a specific year

    Args:
        user_id (int): The user_id to use for the query
        year (int): The year to query

    Returns:
        float: How much the user has spent in a specific year
    """
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31, 23, 59, 59, 59)
    return retrieve_sum_between_date(user_id, start_date, end_date)


def get_last_purchase(user_id: int) -> Purchase:
    """Retrieve the last purchase from a user

    Args:
        user_id (int): The user_id to use for the query

    Returns:
        Purchase: The last purchase from the user
    """
    try:
        return Purchase.objects.filter(user_id=user_id).order_by("-creation_date")[0]
    except DoesNotExist:
        return None
    except IndexError:
        return None


def purchase_exists(message_id: int, chat_id: int) -> None:
    """Check if the message_id is a purchase

    Args:
        message_id (int): The message_id of the purchase

    Returns:
        bool: If The purchase exists
    """
    try:
        return bool(Purchase.objects.get(message_id=message_id, chat_id=chat_id))
    except DoesNotExist:
        return False


def retrieve_sum_between_date(
    user_id: int, start_date: datetime, end_date: datetime, negative: bool = False
) -> float:
    """Retrieve the sum spent between two dates

    Args:
        user_id (int): The user_id to use for the query
        start_date (datetime): The start date
        end_date (datetime): The end date

    Returns:
        float: The sum of all the purchases
    """
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$user_id", "total": {"$sum": "$price"}}},
    ]
    res = list(
        Purchase.objects.filter(creation_date__lte=end_date)
        .filter(creation_date__gte=start_date)
        .aggregate(*pipeline)
    )
    value = -1.0 if negative else 0.0
    return value if len(res) == 0 else res[0]["total"]
