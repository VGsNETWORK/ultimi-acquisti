#!/usr/bin/env python3

from telegram import Update, Message
from telegram.ext import CallbackContext
from root.util.logger import Logger
from root.util.util import is_group_allowed
from root.model.purchase import Purchase
from root.helper.purchase_helper import get_last_purchase
from root.helper.user_helper import user_exists, create_user
from root.contants.messages import ONLY_GROUP, LAST_PURCHASE, NO_PURCHASE

logger = Logger()


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
        context.bot.send_message(chat_id=chat_id, text=ONLY_GROUP, parse_mode="HTML")
        return
    if purchase:
        purchase_chat_id = str(purchase.chat_id).replace("-100", "")
        date = purchase.creation_date
        time = date.strftime("%H:%M")
        date = date.strftime("%d/%m/%Y")
        message = LAST_PURCHASE % (
            user_id,
            first_name,
            date,
            time,
            purchase_chat_id,
            purchase.message_id,
        )
    else:
        message = NO_PURCHASE % (user_id, first_name)
    context.bot.send_message(
        chat_id=chat_id,
        text=message,
        reply_to_message_id=purchase.message_id,
        parse_mode="HTML",
    )