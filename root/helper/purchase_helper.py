#!/usr/bin/env python3

from root.model.purchase import Purchase
from mongoengine.errors import DoesNotExist
from datetime import datetime
from calendar import monthrange
from root.util.logger import Logger
import re

logger = Logger()

def before(start, end, seq):
    open_parens = 0
    for char in seq:
        if char == start:
            open_parens += 1
        elif char == end:
            open_parens -= 1
            if open_parens < 0:
                return False
    return open_parens == 0

def convert_to_float(price: str) -> None:
    logger.info(f"converting {price}")
    dots = re.findall('\.', price)
    commas = re.findall('\,', price)
    apostrophes = re.findall("\'", price)
    if len(commas) == 1 and len(dots) == 1:
        if before(',', '.', price):
            price  = price.replace(',', '')
        else:
            price  = price.replace('.', '').replace(',', '.')
    elif len(commas) == 1 and len(apostrophes) == 1:
        price  = price.replace('\'', '').replace(',', '.')
    elif len(apostrophes) == 1:
        price  = price.replace('\'', '')
    elif len(commas) == 2:
        price = price.replace(',', '', 1).replace(',', '.')
    elif len(dots) == 2:
        price = price.replace('.', '', 1)
    elif len(commas) == 1:
        if len(price.split(',')[1]) > 2:
            price = price.replace(',', '')
        else:
            price = price.replace(',', '.')
    elif len(dots) == 1:
        if len(price.split('.')[1]) > 2:
            price = price.replace('.', '')
    return float(price)

def create_purchase(user_id: int, price: float, message_id: int, chat_id: int) -> None:
    try:
        Purchase.objects.get(message_id=message_id).delete()
    except Exception:
        pass
    Purchase(user_id=user_id, price=price, message_id=message_id, chat_id=chat_id).save()

def retrive_purchases_for_user(user_id: int) -> [Purchase]:
    try:
        return Purchase.objects.filter(user_id=user_id)
    except DoesNotExist:
        return None

def delete_purchase(user_id: int, message_id: int) -> None:
    logger.info(f"finding purchase {message_id} for user {user_id}")
    Purchase.objects.filter(user_id=user_id).get(message_id=message_id).delete()

def retrieve_sum_for_user(user_id: int) -> float:
    pipeline = [{"$match": {"user_id": user_id}}, 
                    {"$group": {"_id": "$user_id", "total": {"$sum": "$price"}}}]
    res = list(Purchase.objects.aggregate(*pipeline))
    return 0.0 if len(res) == 0 else res[0]['total']

def retrieve_sum_for_current_month(user_id: int) -> float:
    return retrieve_sum_for_month(user_id, datetime.now().month)

def retrieve_sum_for_month(user_id: int, month: int) -> float:
    current_date = datetime.now()
    start, end = monthrange(current_date.year, month)
    start_date = datetime(current_date.year, current_date.month, start)
    end_date = datetime(current_date.year, current_date.month, end)
    return retrieve_sum_between_date(user_id, start_date, end_date)

def retrieve_sum_for_current_year(user_id: int) -> float:
    return retrieve_sum_for_year(user_id, datetime.now().year)
    
def retrieve_sum_for_year(user_id: int, year: int) -> float:
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    return retrieve_sum_between_date(user_id, start_date, end_date)
    
def get_last_purchase(user_id: int, chat_id: int = None) -> Purchase:
    try:
        if chat_id:
            return Purchase.objects.filter(user_id=user_id, chat_id=chat_id).order_by("-creation_date")[0]
        else:
            return Purchase.objects.filter(user_id=user_id).order_by("-creation_date")[0]
    except DoesNotExist:
        return None
    except IndexError:
        return None

def retrieve_sum_between_date(user_id: int, start_date: datetime, end_date: datetime) -> float:
    pipeline = [{"$match": {"user_id": user_id }}, 
                {"$group": { "_id": "$user_id" , "total": { "$sum": "$price" }}}]
    res = list(Purchase.objects.filter(creation_date__lte=end_date)\
        .filter(creation_date__gte=start_date).aggregate(*pipeline))
    return 0.0 if len(res) == 0 else res[0]['total']