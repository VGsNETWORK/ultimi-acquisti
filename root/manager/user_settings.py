#!/usr/bin/env python3

from root.contants.keyboard import create_user_settings_keyboard
from root.helper.user_helper import retrieve_user
from root.contants.messages import USER_SETTINGS_HEADER, USER_SETTINGS_MESSAGE
from telegram import Update
from telegram.ext import CallbackContext
from telegram import Message, Chat


def settings_toggle_purchase_tips(update: Update, context: CallbackContext):
    user = update.effective_user
    user = retrieve_user(user.id)
    user.show_purchase_tips = not user.show_purchase_tips
    user.save()
    view_user_settings(update, context)


def view_user_settings(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    chat: Chat = update.effective_chat
    user = update.effective_user
    message_id = message.message_id
    user = retrieve_user(user.id)
    context.bot.edit_message_text(
        message_id=message_id,
        chat_id=chat.id,
        text=USER_SETTINGS_MESSAGE,
        reply_markup=create_user_settings_keyboard(user),
        parse_mode="HTML",
    )
