#!/usr/bin/env python3

from root.model.purchase import Purchase
from mongoengine.errors import DoesNotExist
from datetime import datetime
from calendar import monthrange

def create_purchase(user_id: int, price: float, message_id: int) -> None:
    Purchase(user_id=user_id, price=price, message_id=message_id).save()

def retrive_purchases_for_user(user_id: int) -> [Purchase]:
    try:
        return Purchase.objects.filter(user_id=user_id)
    except DoesNotExist:
        return None

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
    pipeline = [{"$match": {"user_id": user_id }}, 
                {"$group": { "_id": "$user_id" , "total": { "$sum": "$price" }}}]
    res = list(Purchase.objects.filter(creation_date__lte=end_date)\
        .filter(creation_date__gte=start_date).aggregate(*pipeline))
    return 0.0 if len(res) == 0 else res[0]['total']


