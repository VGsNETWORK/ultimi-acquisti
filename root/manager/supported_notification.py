#!/user/bin/env python3
from bot_util.decorator.telegram import update_user_information
from telegram import Update
from telegram.ext import CallbackContext

from root.contants.keyboard import build_notification_choose_section
from root.contants.messages import SUPPORTED_NOTIFICATIONS
from root.helper.admin_message import count_unread_admin_messages_for_user
from root.helper.notification import count_unread_notifications


def show_supported_notifications(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message_id = update.effective_message.message_id
    user = update.effective_user
    nof_notifications = count_unread_notifications(user.id)
    nof_messages = count_unread_admin_messages_for_user(user.id)
    context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=SUPPORTED_NOTIFICATIONS,
        reply_markup=build_notification_choose_section(
            nof_notifications, nof_messages, default=0, supported_notification=True
        ),
        disable_web_page_preview=True,
        parse_mode="HTML",
    )