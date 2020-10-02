#!/usr/bin/env python3

import re
from mongoengine.errors import DoesNotExist
from root.util.logger import Logger
from root.model.purchase import Purchase
from telegram import Update, Message
from root.util.util import is_group_allowed, format_date
from telegram.ext import CallbackContext
from root.contants.messages import (PRICE_MESSAGE_NOT_FORMATTED, PURCHASE_ADDED, ONLY_GROUP,
                                    MONTH_PURCHASES, PRICE_MESSAGE_NOT_FORMATTED, LAST_PURCHASE,
                                    MONTH_PURCHASE_REPORT, PURCHASE_REPORT_TEMPLATE,
                                    YEAR_PURCHASES, CANCEL_PURCHASE_ERROR, NO_PURCHASE,
                                    PURCHASE_NOT_FOUND, PURCHASE_DELETED, PURCHASE_MODIFIED)
from root.util.telegram import TelegramSender
from root.helper.user_helper import user_exists, create_user
from root.helper.purchase_helper import (create_purchase, retrieve_sum_for_current_month, get_last_purchase,
                                         retrive_purchases_for_user, retrieve_month_purchases_for_user,
                                         retrieve_sum_for_current_year, delete_purchase, convert_to_float)

class PurchaseManager:
    def __init__(self):
        self.logger = Logger()
        self.sender = TelegramSender()

    def month_report(self, update: Update, context: CallbackContext) -> None:
        message: Message = update.message if update.message else update.edited_message
        message_id = message.message_id
        chat_id = message.chat.id
        chat_type = message.chat.type
        user = update.effective_user
        user_id = user.id
        if not chat_type == "private":
            if not user_exists(user_id):
                create_user(user)
            if not is_group_allowed(chat_id):
                return
            purchases: [Purchase] = retrieve_month_purchases_for_user(user_id)
        else:
            purchases: [Purchase] = retrive_purchases_for_user(user_id)
        if not purchases:
            message = NO_PURCHASE
        else:
            message = MONTH_PURCHASE_REPORT
            for purchase in purchases:
                template = (PURCHASE_REPORT_TEMPLATE % (str(purchase.chat_id).replace("-100", ""), purchase.message_id, 
                                                       format_date(purchase.creation_date), purchase.price))
                message = f"{message}\n{template}"
        context.bot.send_message(chat_id=chat_id, text=message, 
                                 reply_to_message_id=message_id, parse_mode='HTML')
                    

    
    def last_purchase(self, update: Update, context: CallbackContext) -> None:
        message: Message = update.message if update.message else update.edited_message
        message_id = message.message_id
        chat_id = message.chat.id
        chat_type = message.chat.type
        user = update.effective_user
        user_id = user.id
        if not chat_type == "private":
            if not user_exists(user_id):
                create_user(user)
            if not is_group_allowed(chat_id):
                return
            purchase: Purchase = get_last_purchase(user_id)
        else:
            purchase: Purchase = get_last_purchase(user_id)
        if purchase:
            purchase_chat_id = str(purchase.chat_id).replace("-100", "")
            message = (LAST_PURCHASE % (format_date(purchase.creation_date), purchase_chat_id, purchase.message_id))
        else:
            message = NO_PURCHASE
        context.bot.send_message(chat_id=chat_id, text=message, 
                                 reply_to_message_id=message_id, parse_mode='HTML')
    
    def purchase(self, update: Update, context: CallbackContext) -> None:
        message: Message = update.message if update.message else update.edited_message
        chat_id = message.chat.id
        if message.chat.type == "private":
            context.bot.send_message(chat_id=chat_id, text=ONLY_GROUP, parse_mode='HTML')
            return
        if not is_group_allowed(chat_id):
            return
        message_id = message.message_id
        photo = message.photo
        user = update.effective_user
        message = message.caption
        self.logger.info("Parsing purchase")
        if not photo:
            message = PRICE_MESSAGE_NOT_FORMATTED
            context.bot.send_message(chat_id=chat_id, text=message, 
                                 reply_to_message_id=message_id, parse_mode='HTML')
            return
        try:
            """
            regex: \d+(?:[\.\',]\d{3})?(?:[\.,]\d{1,2}|[\.,]\d{1,2})?
            \d      -> matches a number
            +       -> match one or more of the previous
            ()      -> capturing group
            ?:      -> do not create a capture group (makes no sense but it does not work without)
            [\.\',] -> matches . , '
            \d{3}   -> matches 3 numbers
            ?       -> makes the capturing group optional
            ()      -> capturing group
            ?:      -> do not create a capture group (makes no sense but it does not work without)
            [\.,]   -> marches . or ,
            \d{1,2} -> matches one or two numbers
            ?       -> makes the capturing group optional
            """
            price = re.findall(r"\d+(?:[\.\',]\d{3})?(?:[\.,]\d{1,2})?", message)[0]
            if price:
                price = convert_to_float(price)
                result = {"name": message, "price": price, "error": None}
                self.logger.info(f"The user purchase {price} worth of products")
            else:
                result = {"name": message, "price": 0.00, "error": PRICE_MESSAGE_NOT_FORMATTED}
        except ValueError as ve:
            self.logger.error(ve)
            result = {"name": message, "price": 0.00, "error": PRICE_MESSAGE_NOT_FORMATTED}
        except IndexError as ie:
            self.logger.error(ie)
            result = {"name": message, "price": 0.00, "error": PRICE_MESSAGE_NOT_FORMATTED}
            
        if not result["error"]:
            self.add_purchase(user, price, message_id, chat_id)
            message = PURCHASE_ADDED if update.message else PURCHASE_MODIFIED
        else:
            message = result["error"]
        context.bot.send_message(chat_id=chat_id, text=message, 
                                 reply_to_message_id=message_id, parse_mode='HTML')
    
    def month_purchase(self, update: Update, context: CallbackContext) -> None:
        # TODO: Controllare se il messaggio viene da un gruppo o una chat privata
        message: Message = update.message if update.message else update.edited_message
        chat_id = message.chat.id
        if not is_group_allowed(chat_id):
            return
        user_id = update.effective_user.id
        price  = retrieve_sum_for_current_month(user_id)
        message = (MONTH_PURCHASES % (f"%.2f" % price))
        self.send_purchase(update, context, price, message)
        
    def year_purchase(self, update: Update, context: CallbackContext) -> None:
        # TODO: Controllare se il messaggio viene da un gruppo o una chat privata
        message: Message = update.message if update.message else update.edited_message
        chat_id = message.chat.id
        if not is_group_allowed(chat_id):
            return
        user_id = update.effective_user.id
        price  = retrieve_sum_for_current_year(user_id)
        message = (YEAR_PURCHASES % (f"%.2f" % price))
        self.send_purchase(update, context, price, message)
        
    def send_purchase(self, update: Update, context: CallbackContext, price: float, message: str) -> None:
        chat_id = update.message.chat.id
        telegram_message: Message = update.message if update.message else update.edited_message
        message_id = telegram_message.message_id
        context.bot.send_message(chat_id=chat_id, text=message, 
                                 reply_to_message_id=message_id, parse_mode='HTML')
    
    def add_purchase(self, user, price, message_id, chat_id):
        if not user_exists(user.id):
            create_user(user)
        create_purchase(user.id, price, message_id, chat_id)

    def delete_purchase(self, update: Update, context: CallbackContext):
        # TODO: Controllare se il messaggio viene da un gruppo o una chat privata
        message: Message = update.message if update.message else update.edited_message
        chat_id = message.chat.id
        if not is_group_allowed(chat_id):
            return
        message: Message = update.message if update.message else update.edited_message
        reply = message.reply_to_message
        user_id = update.effective_user.id
        chat_id = message.chat.id
        message_id = message.message_id
        if not reply:
            context.bot.send_message(chat_id=chat_id, text=CANCEL_PURCHASE_ERROR, 
                                 reply_to_message_id=message_id, parse_mode='HTML')
            return
        try:
            message_id = reply.message_id
            delete_purchase(user_id, message_id)
            context.bot.send_message(chat_id=chat_id, text=PURCHASE_DELETED, 
                                 reply_to_message_id=message_id, parse_mode='HTML')
        except DoesNotExist:
            message_id = message.message_id
            context.bot.send_message(chat_id=chat_id, text=PURCHASE_NOT_FOUND, 
                                 reply_to_message_id=message_id, parse_mode='HTML')



        