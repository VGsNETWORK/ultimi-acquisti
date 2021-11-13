#!/usr/bin/env python3

from telegram import Update
from telegram.ext import CallbackContext

from root.contants.messages import SECTION_LOCKED_MESSAGE


def show_section_locked_popup(update: Update, context: CallbackContext):
    context.bot.answer_callback_query(
        update.callback_query.id, text=SECTION_LOCKED_MESSAGE, show_alert=True
    )
