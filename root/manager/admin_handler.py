#!/usr/bin/env python3

from root.contants.messages import USER_INFO_RECAP_LEGEND
from root.util.util import create_button
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from root.helper.aggregation.user_info import USER_INFO_NATIVE_QUERY
from telegram import Update
from telegram.ext import CallbackContext
from root.model.subscriber import Subscriber
import telegram_utils.utils.logger as logger


def handle_admin(update: Update, context: CallbackContext):
    cursor = Subscriber.objects.aggregate(USER_INFO_NATIVE_QUERY)
    message = ""
    for result in cursor:
        if "last_name" in result:
            name = "%s %s" % (result["first_name"], result["last_name"])
        else:
            name = "%s" % (result["first_name"])
        line = '<a href="tg://user?id=%s">%s  (@%s)</a>' % (
            result["user_id"],
            name,
            result["username"],
        )
        line += "\n    🗃  <code>%s</code>" % result["wishlists"]
        line += "\n     │"
        line += "\n     └─🗂  <code>%s</code>" % result["wishlist_elements"]
        line += "\n            │"
        line += "\n            ├─🖼  <code>%s</code>" % result["photos"]
        line += "\n            │"
        line += "\n            └─🔗  <code>%s</code>" % result["links"]
        line += "\n                   │"
        line += "\n                   └─💹  <code>%s</code>" % result["tracked_links"]
        line += "\n\n\n"
        message += line
    message += USER_INFO_RECAP_LEGEND
    keyboard = InlineKeyboardMarkup(
        [[create_button("↩️  Torna indietro", "cancel_rating", "")]]
    )
    context.bot.edit_message_text(
        message_id=update.effective_message.message_id,
        chat_id=update.effective_chat.id,
        text=message,
        disable_web_page_preview=True,
        reply_markup=keyboard,
        parse_mode="HTML",
    )
    return context.bot.answer_callback_query(update.callback_query.id)