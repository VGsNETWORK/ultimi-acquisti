#!/usr/bin/env python3

from telegram.ext.conversationhandler import ConversationHandler
from root.helper.user_helper import change_wishlist
from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update
from root.manager.wishlist_element import (
    ask_delete_all_wishlist_elements,
    confirm_delete_all_wishlist_elements,
    view_wishlist,
)


def view_wishlist_conv_end(update: Update, context: CallbackContext):
    view_wishlist(update, context, reset_keyboard=False)
    return ConversationHandler.END


def change_current_wishlist(update: Update, context: CallbackContext):
    wishlist_id = update.callback_query.data.split("_")[-1]
    user_id = update.effective_user.id
    change_wishlist(user_id, wishlist_id)
    update.callback_query.data += "_0"
    view_wishlist(update, context, page=0, reset_keyboard=False)


def ask_delete_wishlist_list(update: Update, context: CallbackContext):
    ask_delete_all_wishlist_elements(update, context, True)


def confirm_delete_wishlist_list(update: Update, context: CallbackContext):
    confirm_delete_all_wishlist_elements(update, context, True)