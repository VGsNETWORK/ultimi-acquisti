#!/usr/bin/env python3

import re
from root.util.logger import Logger
from telegram import Update
from telegram.ext import CallbackContext
from root.contants.messages import PRICE_MESSAGE_NOT_FORMATTED, PURCHASE_ADDED, MONTH_PURCHASES, PRICE_MESSAGE_NOT_FORMATTED
from root.util.telegram import TelegramSender
from root.helper.user_helper import user_exists, create_user
from root.helper.purchase_helper import create_purchase, retrieve_sum_for_current_month

class PurchaseManager:
    def __init__(self):
        self.logger = Logger()
        self.sender = TelegramSender()
    
    def purchase(self, update: Update, context: CallbackContext) -> None:
        self.logger.info("Parsing purchase")
        chat_id = update.message.chat.id
        message_id = update.message.message_id
        photo = update.message.photo
        user = update.effective_user
        message = update.message.caption
        if not photo:
            message = PRICE_MESSAGE_NOT_FORMATTED
            context.bot.send_message(chat_id=chat_id, text=message, 
                                 reply_to_message_id=message_id, parse_mode='HTML')
            return
        try:
            price = re.sub(",", ".", message)
            price = re.sub("€", " ", price)
            price = re.sub("\#ultimiacquisti ", "", price)
            price = float(price)
            result = {"name": message, "price": price, "error": None}
            self.logger.info(f"The user purchase {price} worth of products")
        except ValueError:
            result= {"name": message, "price": 0.00, "error": PRICE_MESSAGE_NOT_FORMATTED}
        
        if not result["error"]:
            self.add_purchase(user, price)
        message = result["error"] if result["error"] else PURCHASE_ADDED
        context.bot.send_message(chat_id=chat_id, text=message, 
                                 reply_to_message_id=message_id, parse_mode='HTML')
    
    def month_purchase(self, update: Update, context: CallbackContext) -> None:
        chat_id = update.message.chat.id
        user_id = update.effective_user.id
        message_id = update.message.message_id
        price  = retrieve_sum_for_current_month(user_id)
        message = (MONTH_PURCHASES % (f"%.2f" % price))
        context.bot.send_message(chat_id=chat_id, text=message, 
                                 reply_to_message_id=message_id, parse_mode='HTML')
    
    def add_purchase(self, user, price):
        if not user_exists(user.id):
            create_user(user)
        create_purchase(user.id, price)
        