#!/usr/bin/env python3


from urllib.parse import quote
from root.helper.wishlist import find_wishlist_by_id
from root.model.wishlist import Wishlist
from root.util.util import create_button
from telegram import Update
from telegram.chat import Chat
from telegram.ext import CallbackContext
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.message import Message


def ask_confirm_deletion(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    chat: Chat = update.effective_chat
    context.bot.answer_callback_query(update.callback_query.id)
    message_id = message.message_id
    _id = update.callback_query.data.split("_")[-1]
    page = int(update.callback_query.data.split("_")[-2])
    index = update.callback_query.data.split("_")[-3]
    message = f"<b><u>LISTA DEI DESIDERI</u></b>\n\n\n"
    append = "🔄  <i>Stai per convertire questo elemento in un acquisto</i>"
    wish: Wishlist = find_wishlist_by_id(_id)
    if wish.link:
        message += f'<b>{index}</b>  <a href="{wish.link}">{wish.description}</a>\n{append}\n\n'
    else:
        message += f"<b>{index}</b>  {wish.description}\n{append}\n\n"
    message += (
        "<b>Vuoi continuare?</b>\n<i>Questa azione è irreversibile"
        " e cancellerà l'elemento dalla lista dei desideri.</i>"
    )
    keyboard = InlineKeyboardMarkup(
        [
            [
                create_button(
                    "🤍  🔄  🛍",
                    f"delete_wish_and_create_purchase_link_{page}_{_id}",
                    f"delete_wish_and_create_purchase_link_{page}_{_id}",
                ),
            ],
            [
                create_button(
                    "❌  Annulla",
                    f"view_wishlist_{page}",
                    f"view_wishlist_{page}",
                ),
            ],
        ]
    )
    context.bot.edit_message_text(
        chat_id=chat.id,
        message_id=message_id,
        text=message,
        reply_markup=keyboard,
        disable_web_page_preview=True,
        parse_mode="HTML",
    )


def wishlist_confirm_convertion(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    chat: Chat = update.effective_chat
    message_id = message.message_id
    context.bot.answer_callback_query(update.callback_query.id)
    _id = update.callback_query.data.split("_")[-1]
    wish: Wishlist = find_wishlist_by_id(_id)
    page = int(update.callback_query.data.split("_")[-2])
    wish_description = wish.description
    if wish.link:
        wish_description = '<a href="%s">%s</a>' % (wish.link, wish_description)
    url = (
        "https://t.me/share/url?url=%23ultimiacquisti%20%3C"
        f"prezzo%3E%20%3CDD%2FMM%2FYY%28YY%29%3E%0A%0A%25{quote(wish.description)}%25"
    )
    wish.delete()
    keyboard = InlineKeyboardMarkup(
        [
            [
                create_button(
                    "🛍  Registra l'acquisto",
                    f"convert_and_do_a_barrel_roll",
                    f"convert_and_do_a_barrel_roll",
                    url,
                ),
            ],
            [
                create_button(
                    "↩️  Torna indietro",
                    f"view_wishlist_{page}",
                    f"view_wishlist_{page}",
                ),
            ],
        ]
    )
    message = f"<b><u>LISTA DEI DESIDERI</u></b>\n\n\n"
    message += (
        "😃  Link di acquisto per <b>%s</b> creato!\n\nPuoi registrare il tuo nuovo acquisto"
        " premendo il tasto sottostante e selezionando un gruppo <b><u>dove sono presente</u></b>."
        % wish_description
    )
    context.bot.edit_message_text(
        chat_id=chat.id,
        message_id=message_id,
        text=message,
        reply_markup=keyboard,
        disable_web_page_preview=True,
        parse_mode="HTML",
    )