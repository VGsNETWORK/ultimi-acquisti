#!/usr/bin/env python3

import re
from mongoengine.errors import DoesNotExist
from root.util.logger import Logger
from root.model.purchase import Purchase
from telegram import Update, Message
from root.util.util import is_group_allowed, format_date, get_current_month, get_current_year, get_month_string
from telegram.ext import CallbackContext
from root.contants.messages import (PRICE_MESSAGE_NOT_FORMATTED, PURCHASE_ADDED, ONLY_GROUP,
                                    MONTH_PURCHASES, LAST_PURCHASE,
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
        chat_id = message.chat.id
        chat_type = message.chat.type
        user = update.effective_user
        first_name = user.first_name
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
            message = NO_PURCHASE % (user_id, first_name)
        else:
            message = MONTH_PURCHASE_REPORT % (user_id, first_name)
            for purchase in purchases:
                template = (PURCHASE_REPORT_TEMPLATE % (str(purchase.chat_id).replace("-100", ""), purchase.message_id, 
                                                       format_date(purchase.creation_date, False), (f"%.2f" % purchase.price)))
                message = f"{message}\n{template}"
        context.bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
                    

    
    def last_purchase(self, update: Update, context: CallbackContext) -> None:
        message: Message = update.message if update.message else update.edited_message
        chat_id = message.chat.id
        chat_type = message.chat.type
        user = update.effective_user
        user_id = user.id
        first_name = user.first_name
        if not chat_type == "private":
            if not user_exists(user_id):
                create_user(user)
            if not is_group_allowed(chat_id):
                return
            purchase: Purchase = get_last_purchase(user_id)
        else:
            context.bot.send_message(chat_id=chat_id, text=ONLY_GROUP, parse_mode='HTML')
            return
        if purchase:
            purchase_chat_id = str(purchase.chat_id).replace("-100", "")
            message = (LAST_PURCHASE % (user_id, first_name, format_date(purchase.creation_date), purchase_chat_id, purchase.message_id))
        else:
            message = NO_PURCHASE % (user_id, first_name)
        context.bot.send_message(chat_id=chat_id, text=message, 
                                 reply_to_message_id=purchase.message_id, parse_mode='HTML')
    
    def purchase(self, update: Update, context: CallbackContext) -> None:
        message: Message = update.message if update.message else update.edited_message
        chat_id = message.chat.id
        if message.chat.type == "private":
            context.bot.send_message(chat_id=chat_id, text=ONLY_GROUP, parse_mode='HTML')
            return
        if not is_group_allowed(chat_id):
            return
        message_id = message.message_id
        user = update.effective_user
        message = message.caption
        self.logger.info("Parsing purchase")
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
                result = {"name": message, "price": 0.00, "error": None}
        except ValueError as ve:
            self.logger.error(ve)
            # TODO: send to log channel
            return
        except IndexError as ie:
            self.logger.error(ie)
            # TODO: send to log channel
            return

        if not result["error"]:
            self.add_purchase(user, price, message_id, chat_id)
            message = PURCHASE_ADDED if update.message else PURCHASE_MODIFIED
        else:
            message = result["error"]
        context.bot.send_message(chat_id=chat_id, text=message, 
                                 reply_to_message_id=message_id, parse_mode='HTML')
    
    def month_purchase(self, update: Update, context: CallbackContext) -> None:
        message: Message = update.message if update.message else update.edited_message
        chat_id = message.chat.id
        chat_type = message.chat.type
        user = message.from_user
        user_id = user.id
        first_name = user.first_name
        if not chat_type == "private":
            if not user_exists(user_id):
                create_user(user)
            if not is_group_allowed(chat_id):
                return
        price  = retrieve_sum_for_current_month(user_id)
        date = f"{get_current_month( False, True)} {get_current_year()}"
        message = (MONTH_PURCHASES % (user_id, first_name, date, (f"%.2f" % price)))
        self.send_purchase(update, context, price, message)
        
    def year_purchase(self, update: Update, context: CallbackContext) -> None:
        message: Message = update.message if update.message else update.edited_message
        chat_id = message.chat.id
        user = message.from_user
        user_id = user.id
        first_name = user.first_name
        chat_type = message.chat.type
        if not chat_type == "private":
            if not user_exists(user_id):
                create_user(user)
            if not is_group_allowed(chat_id):
                return
        user_id = update.effective_user.id
        first_name = update.effective_user.first_name
        price  = retrieve_sum_for_current_year(user_id)
        message = (YEAR_PURCHASES % (user_id, first_name, get_current_year(), (f"%.2f" % price)))
        self.send_purchase(update, context, price, message)
        
    def send_purchase(self, update: Update, context: CallbackContext, price: float, message: str) -> None:
        telegram_message: Message = update.message if update.message else update.edited_message
        chat_id = telegram_message.chat.id
        context.bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
    
    def add_purchase(self, user, price, message_id, chat_id):
        if not user_exists(user.id):
            create_user(user)
        create_purchase(user.id, price, message_id, chat_id)

    def delete_purchase(self, update: Update, context: CallbackContext):
        message: Message = update.message if update.message else update.edited_message
        chat_id = message.chat.id
        user = message.from_user
        user_id = user.id
        first_name = user.first_name
        chat_type = message.chat.type
        if not chat_type == "private":
            if not user_exists(user_id):
                create_user(user)
            if not is_group_allowed(chat_id):
                return
        message: Message = update.message if update.message else update.edited_message
        reply = message.reply_to_message
        user_id = update.effective_user.id
        chat_id = message.chat.id
        first_name = update.effective_user.first_name
        message_id = message.message_id
        if not reply:
            message = CANCEL_PURCHASE_ERROR % (user_id, first_name)
            context.bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
            return
        try:
            message_id = reply.message_id
            delete_purchase(user_id, message_id)
            context.bot.send_message(chat_id=chat_id, text=PURCHASE_DELETED, parse_mode='HTML')
        except DoesNotExist:
            message_id = message.message_id
            message = CANCEL_PURCHASE_ERROR % (user_id, first_name)
            context.bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')



        