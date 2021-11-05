#!/usr/bin/env python3
from typing import List
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from root.contants.messages import (
    PLEASE_NOTE_APPEND,
    START_COMMAND,
    build_show_notification_button,
)
from root.helper.start_messages import get_start_messages
from root.helper.user_helper import is_admin
from root.model.start_messages import StartMessages
from telegram.bot import Bot
from telegram_utils.utils.misc import environment
from telegram.error import BadRequest
import telegram_utils.utils.logger as logger
from datetime import datetime
from root.util.util import create_button

current_year = datetime.now().year


def update_start_messages():
    messages: List[StartMessages] = get_start_messages()
    for message in messages:
        message_id = message.message_id
        user_id = message.user_id
        first_name = message.first_name
        token = environment("TOKEN")
        bot: Bot = Bot(token)
        text = f"{START_COMMAND}" % (user_id, first_name, PLEASE_NOTE_APPEND)
        try:
            bot.edit_message_text(
                chat_id=user_id,
                message_id=message_id,
                text=text,
                reply_markup=build_keyboard(user_id),
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
        except BadRequest:
            logger.info(f"unable to edit message_id {message_id} for {user_id}")


def build_keyboard(user_id: int):
    if is_admin(user_id):
        logger.info("User [%s] is an admin" % user_id)
        admin_button = [
            create_button(
                "🎖 PANNELLO ADMIN",
                "show_admin_panel",
                "show_admin_panel",
            ),
            create_button(
                "⚙️  Impostazioni",
                "user_settings",
                "user_settings",
            ),
        ]
    else:
        logger.info("User [%s] is NOT an admin" % user_id)
        admin_button = [
            create_button(
                "⚙️  Impostazioni",
                "user_settings",
                "user_settings",
            )
        ]
    return InlineKeyboardMarkup(
        [
            [
                create_button(
                    "🔻     Mostra i comandi     🔻",
                    "start_show_commands",
                    "start_show_commands",
                )
            ],
            [create_button("📚  Guida all'utilizzo", "how_to_page_0", "how_to_page_0")],
            [
                create_button(
                    build_show_notification_button(user_id=user_id),
                    "go_to_notification_section",
                    "go_to_notification_section",
                )
            ],
            [
                create_button("📈  Report mensile", "expand_report", "expand_report"),
                create_button(
                    "💡 Che cos'è?", "monthly_report_info", "monthly_report_info"
                ),
            ],
            [
                create_button(
                    "📈  Report annuale",
                    f"expand_year_report_{current_year}",
                    f"expand_year_report_{current_year}",
                ),
                create_button(
                    "💡 Che cos'è?", "yearly_report_info", "yearly_report_info"
                ),
            ],
            [
                create_button(
                    "♥️  Lista dei desideri",
                    "view_wishlist_element_0",
                    "view_wishlist_element_0",
                )
            ],
            admin_button,
            [
                create_button(
                    "ℹ️  Info",
                    "show_bot_info",
                    "show_bot_info",
                ),
                create_button(
                    "⭐  Valutami",
                    "rating_menu",
                    "rating_menu",
                ),
            ],
            [
                create_button(
                    "🆘  Supporto",
                    "send_feedback",
                    "send_feedback",
                    # url="t.me/VGsNETWORK_Bot?start=leave_feedback",
                )
            ],
        ]
    )
