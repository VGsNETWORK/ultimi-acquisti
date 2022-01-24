#!/usr/bin/env python3

from telegram.ext.conversationhandler import ConversationHandler
from root.contants.messages import NOTIFICATION_WISHLIST_CHANGED
from root.helper.notification import create_notification
from root.helper.user_helper import change_wishlist, retrieve_user
from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update
from root.helper.wishlist import find_default_wishlist, find_wishlist_by_id
from root.manager.wishlist_element import (
    ask_delete_all_wishlist_elements,
    confirm_delete_all_wishlist_elements,
    view_wishlist,
)
from root.model.wishlist import Wishlist
from bot_util.decorator.maintenance import check_maintenance


@check_maintenance
def view_wishlist_conv_end(update: Update, context: CallbackContext):
    update.callback_query.data += "_0"
    view_wishlist(update, context, reset_keyboard=False)
    return ConversationHandler.END


@check_maintenance
def change_current_wishlist(update: Update, context: CallbackContext):
    wishlist_id = update.callback_query.data.split("_")[-1]
    user_id = update.effective_user.id
    db_user = retrieve_user(user_id)
    current_wishlist_id = db_user.current_wishlist
    current_wishlist: Wishlist = find_wishlist_by_id(current_wishlist_id)
    previous_name = current_wishlist.title
    new_wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
    new_name = new_wishlist.title
    change_wishlist(user_id, wishlist_id)
    update.callback_query.data += "_0"
    notification_message = NOTIFICATION_WISHLIST_CHANGED % (previous_name, new_name)
    if not wishlist_id == current_wishlist_id:
        create_notification(user_id, notification_message)
    view_wishlist(update, context, page=0, reset_keyboard=True)


@check_maintenance
def ask_delete_wishlist_list(update: Update, context: CallbackContext):
    ask_delete_all_wishlist_elements(update, context, True)


@check_maintenance
def confirm_delete_wishlist_list(update: Update, context: CallbackContext):
    confirm_delete_all_wishlist_elements(update, context, True)
