#!/usr/bin/env python3


from telegram.update import Update
from root.contants.message_timeout import FIFTEEN_MINUTES
from telegram.message import Message
from root.contants.messages import ADS_MESSAGES
from telegram.ext.callbackcontext import CallbackContext
import random
from time import sleep
from telegram_utils.utils.tutils import send_and_delete


def send_advertisement(context: CallbackContext, group_id: int = None):
    if not group_id:
        args: dict = context.job.context
        group_id: int = args["group"]
    message = random.choice(ADS_MESSAGES)
    send_and_delete(group_id, message, timeout=FIFTEEN_MINUTES)


def command_send_advertisement(update: Update, context: CallbackContext):
    send_advertisement(context, update.effective_chat.id)