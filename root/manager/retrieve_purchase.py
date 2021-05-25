#!/usr/bin/env python3

from telegram.chat import Chat
from root.util.util import format_error
from root.helper.user_helper import is_admin
from telegram import Update
from telegram.ext.callbackcontext import CallbackContext
from root.manager.purchase.handle_purchase import handle_purchase
from pyrogram import Client
from pyrogram.types.messages_and_media.message import Message
from telegram_utils.utils.misc import environment
from root.helper.purchase_helper import find_by_message_id_and_chat_id
import telegram_utils.utils.logger as logger


def check_message(message: Message, client: Client):
    message_id = message.message_id
    chat_id = message.chat.id
    if not find_by_message_id_and_chat_id(message_id, chat_id):
        handle_purchase(client, message, False)
        return True
    return False


def get_messages_for(chat_id: int, client: Client):
    purchases_added = {}
    chat: Chat = client.get_chat(chat_id)
    group_name = chat.title.split(" | ")[0]
    for message in client.search_messages(chat_id):
        message: Message = message
        text: str = message.text if message.text else message.caption
        if text:
            if "#ultimiacquisti" in text:
                if check_message(message, client):
                    user_id = message.from_user.id
                    first_name = message.from_user.first_name
                    user_id = str(user_id)
                    if user_id in purchases_added:
                        purchases_added[user_id]["purchases_added"] += 1
                    else:
                        purchases_added[user_id] = {}
                        purchases_added[user_id]["purchases_added"] = 1
                        purchases_added[user_id]["first_name"] = first_name
    append = (
        "Ecco il recap degli acquisti importati per il gruppo <i>%s</i>:\n" % group_name
    )
    if purchases_added:
        for user_id in purchases_added:
            first_name = purchases_added[user_id]["first_name"]
            total_purchases_added = purchases_added[user_id]["purchases_added"]
            append += '    –  <code>%s</code>  acquisti per <a href="tg://user?id=%s">%s</a>\n' % (
                total_purchases_added,
                user_id,
                first_name,
            )
    else:
        append += "\n<i>Non sono stati trovati acquisti da importare!</i>"
    return append


def update_purchases_for_chat(update: Update, context: CallbackContext):
    chat_type = update.effective_chat.type
    if chat_type == "private":
        return
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
    api_id = environment("API_ID")
    api_hash = environment("API_HASH")
    client: Client = Client("retrieve_product", api_id=api_id, api_hash=api_hash)
    try:
        client.start()
        chat_id = update.effective_chat.id
        append = get_messages_for(chat_id, client)
        log_channel = environment("ERROR_CHANNEL")
        context.bot.send_message(
            chat_id=log_channel,
            text=append,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except Exception as e:
        e = format_error(e)
        logger.error(e)
    finally:
        client.stop()