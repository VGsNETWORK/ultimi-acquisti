#!/usr/bin/env python3

from telegram import Update
from telegram.ext import CallbackContext
from root.contants.messages import SECTION_LOCKED_MESSAGE, USER_REPUTATION_GRADES_LIST
from bot_util.helper.user.user_reputation import (
    get_user_reputation,
    visualize_user_reputation,
)
from bot_util.decorator.maintenance import check_maintenance


@check_maintenance
def show_section_locked_popup(update: Update, context: CallbackContext):
    user_reputation = get_user_reputation(update.effective_user.id)
    visualization = visualize_user_reputation(user_reputation)
    user_reputation = USER_REPUTATION_GRADES_LIST[user_reputation]
    message = SECTION_LOCKED_MESSAGE % (visualization, user_reputation)
    context.bot.answer_callback_query(
        update.callback_query.id,
        text=message,
        show_alert=True,
    )
