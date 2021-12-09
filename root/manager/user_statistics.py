#!/usr/bin/env python3

from bot_util.helper.user.user import (
    count_users,
    find_user,
    find_user_paged,
    find_user_index,
)
from bot_util.model.button import Button
from bot_util.model.button_selected import SelectedButton
from telegram import Update
from telegram.ext import CallbackContext
from bot_util.helper.user.user_statistics import build_user_statistics_lib_keyboard
from bot_util.decorator.telegram import update_user_information
from telegram import InlineKeyboardMarkup
from bot_util.helper.redis import save_value_to_redis
from bot_util.constant.user_statistics import PREVIOUS_CALLBACK_KEY
from telegram.user import User
import telegram_utils.utils.logger as logger
from root.model.wishlist import Wishlist
from root.helper.aggregation.user_info import (
    USER_INFO_NATIVE_QUERY,
    build_all_user_info_query,
)
from root.util.util import (
    retrieve_telegram_user,
)

from root.contants.messages import (
    GO_BACK_BUTTON_TEXT,
    WISHLIST_BUTTON_TEXT,
)
from telegram.error import BadRequest
import telegram_utils.helper.redis as redis_helper

from root.contants.messages import (
    ADMIN_PANEL_COMMUNICATION_STATS_MESSAGE,
    GO_BACK_BUTTON_TEXT,
    NEVER_INTERACTED_WITH_THE_BOT_MESSAGE,
    USER_INFO_RECAP_LEGEND,
    WISHLIST_BUTTON_TEXT,
)
from bot_util.model.user import User as DbUser

from pymongo.command_cursor import CommandCursor


def save_to_redis(user_id: int, value: str):
    save_value_to_redis(PREVIOUS_CALLBACK_KEY % user_id, value)


def find_users(user: DbUser, index: int):
    """ Find the previous and next user after one in the database """
    prev: DbUser = find_user_paged(index + 1)
    next: DbUser = find_user_paged(index - 1)
    prev = prev[0] if prev else None
    next = next[0] if next else None
    return prev, next


def build_user_wishlist_info_keyboard(
    user: DbUser, prev: DbUser, next: DbUser, index: int
):
    """ Build the keyboard responsible to navigate between users """
    if prev:
        first_name = prev.first_name if prev.first_name else "Sconosciuto"
        prev_text = f"►   {first_name}"
        prev_callback = "show_usage" + f"_{prev.user_id}_{index + 1}"
    else:
        prev_text = "🔚"
        prev_callback = "empty_button"
    if next:
        first_name = next.first_name if next.first_name else "Sconosciuto"
        next_text = f"{first_name}   ◄"
        next_callback = "show_usage" + f"_{next.user_id}_{index - 1}"
    else:
        next_text = "🔚"
        next_callback = "empty_button"

    middle_callback = "empty_button"
    middle_text = "%s/%s" % (index + 1, count_users())
    return [
        Button(next_text, next_callback),
        Button(middle_text, middle_callback),
        Button(prev_text, prev_callback),
    ]


def get_buttons():
    previous_buttons = [[Button(WISHLIST_BUTTON_TEXT, "view_wishlist_stastics")]]
    go_back_button = Button(GO_BACK_BUTTON_TEXT, "show_admin_panel")
    return previous_buttons.copy(), go_back_button


def build_keyboard(update: Update, context: CallbackContext, user: DbUser, index: int):
    previous_buttons, go_back_button = get_buttons()
    previous_buttons.append(
        build_user_wishlist_info_keyboard(user, *find_users(user, index), index)
    )
    save_to_redis(update.effective_user.id, update.callback_query.data)
    keyboard: InlineKeyboardMarkup = build_user_statistics_lib_keyboard(
        previous_buttons,
        go_back_button,
        SelectedButton(0, 0),
        update.effective_user.id,
        [1],
    )
    return keyboard


def build_cursor(user: DbUser):
    return [
        {
            "user_id": user.user_id,
            "tracked_links": 0,
            "wishlist_elements": 0,
            "links": 0,
            "photos": 0,
            "wishlists": 0,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
        }
    ]


def user_statistics(update: Update, context: CallbackContext):
    context.bot.answer_callback_query(update.callback_query.id)
    data = update.callback_query.data
    user_id = data.split("_")[-2]
    user_index = data.split("_")[-1]
    if not user_index.isdigit():
        user_index = 0
    else:
        user_index = int(user_index)
    logger.info("running query for user_id %s" % user_id)
    db_user: DbUser = (
        find_user(user_id=user_id) if user_id.isdigit() else find_user_paged()[0]
    )
    cursor: CommandCursor = Wishlist.objects.aggregate(
        build_all_user_info_query(db_user.user_id)
    )
    message = ""
    results = list(cursor)
    if len(results) == 0:
        results = build_cursor(db_user)
    for result in results:
        try:
            user: User = retrieve_telegram_user(result["user_id"])
            if user:
                username = user.username
                first_name = user.first_name if user.first_name else ""
                last_name = user.last_name if user.last_name else ""
                if "last_name" in result:
                    name = "%s %s" % (first_name, last_name)
                else:
                    name = "%s" % (first_name)
            else:
                name = NEVER_INTERACTED_WITH_THE_BOT_MESSAGE
                username = ""
        except KeyError:
            name = NEVER_INTERACTED_WITH_THE_BOT_MESSAGE
            username = ""
        try:
            if username:
                line = '<a href="tg://user?id=%s">%s  (@%s)</a>' % (
                    result["user_id"],
                    name,
                    username,
                )
            else:
                line = '<a href="tg://user?id=%s">%s</a>' % (
                    result["user_id"],
                    name,
                )
        except KeyError:
            line = '<a href="tg://user?id=%s">%s</a>' % (
                result["user_id"],
                name,
            )
        line += "\n    🗃  <code>%s</code>" % result["wishlists"]
        line += "\n     │"
        line += "\n     └──🗂  <code>%s</code>" % result["wishlist_elements"]
        line += "\n               │"
        line += "\n               ├──🖼  <code>%s</code>" % result["photos"]
        line += "\n               └──🔗  <code>%s</code>" % result["links"]
        line += "\n                         │"
        line += (
            "\n                         └──💹  <code>%s</code>" % result["tracked_links"]
        )
        line += "\n\n\n"
        message += line
    message += USER_INFO_RECAP_LEGEND
    message = f"{ADMIN_PANEL_COMMUNICATION_STATS_MESSAGE}{message}"
    keyboard = build_keyboard(update, context, db_user, user_index)
    try:
        context.bot.edit_message_text(
            message_id=update.effective_message.message_id,
            chat_id=update.effective_chat.id,
            text=message,
            disable_web_page_preview=True,
            reply_markup=keyboard,
            parse_mode="HTML",
        )
    except BadRequest:
        user = update.effective_user
        try:
            context.bot.edit_message_text(
                message_id=redis_helper.retrieve(
                    "%s_%s_admin" % (user.id, user.id)
                ).decode(),
                chat_id=update.effective_chat.id,
                text=message,
                disable_web_page_preview=True,
                reply_markup=keyboard,
                parse_mode="HTML",
            )
        except Exception as e:
            logger.error(e)
    return context.bot.answer_callback_query(update.callback_query.id)
