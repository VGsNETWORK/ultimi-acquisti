#!/usr/bin/env python3

from root.manager.command_redirect import command_redirect
from telegram_utils.utils.tutils import delete_if_private
from root.contants.keyboard import create_user_settings_keyboard
from root.helper.user_helper import create_user, retrieve_user
from root.contants.messages import USER_SETTINGS_HEADER, USER_SETTINGS_MESSAGE
from telegram import Update
from telegram.ext import CallbackContext
from telegram import Message, Chat
from root.util.telegram import TelegramSender

sender = TelegramSender()


def settings_toggle_purchase_tips(update: Update, context: CallbackContext):
    user = update.effective_user
    user = retrieve_user(user.id)
    user.show_purchase_tips = not user.show_purchase_tips
    user.save()
    view_user_settings(update, context)


def view_user_settings(update: Update, context: CallbackContext):
    if not update.effective_message.chat.type == "private":
        command_redirect("impostazioni", "show_settings", update, context)
        return
    message: Message = update.effective_message
    if not update.callback_query:
        sender.delete_if_private(context, message)
    if message.chat.type == "private":
        chat: Chat = update.effective_chat
        user = update.effective_user
        message_id = message.message_id
        user = retrieve_user(user.id)
        if not user:
            user = update.effective_user
            create_user(user)
            user = retrieve_user(user.id)
        if update.callback_query:
            context.bot.edit_message_text(
                message_id=message_id,
                chat_id=chat.id,
                text=USER_SETTINGS_MESSAGE,
                reply_markup=create_user_settings_keyboard(user),
                parse_mode="HTML",
            )
        else:
            sender.delete_previous_message(
                update.effective_user.id,
                update.effective_message.message_id,
                update.effective_chat.id,
                context,
            )
            context.bot.send_message(
                chat_id=chat.id,
                text=USER_SETTINGS_MESSAGE,
                reply_markup=create_user_settings_keyboard(user),
                parse_mode="HTML",
            )
