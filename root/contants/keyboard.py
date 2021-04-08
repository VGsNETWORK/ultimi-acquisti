#!/usr/bin/env python3

from root.contants.messages import BOT_NAME
from telegram import InlineKeyboardMarkup
from root.util.util import create_button


def send_command_to_group_keyboard(command: str, args: str = "", custom: bool = False):
    if not custom:
        command = f"t.me/share/url?url={command}%40{BOT_NAME}{args}"
    text = "☝🏻 Seleziona un gruppo"
    return InlineKeyboardMarkup(
        [
            [
                create_button(
                    text, "send_command_to_group", "send_command_to_group", command
                ),
            ]
        ]
    )


NEW_PURCHASE_TEMPLATE = (
    "%23ultimiacquisti%20%3Cprezzo%3E%20%3CDD%2FMM%2FYYYY%3E%0A%0A%25%3Ctitolo%3E%25"
)
NEW_PURCHASE_LINK = "https://t.me/share/url?url=%23ultimiacquisti%20%3Cprezzo%3E%20%3CDD%2FMM%2FYYYY%3E%0A%0A%25%3Ctitolo%3E%25"

NO_PURCHASE_KEYBOARD = InlineKeyboardMarkup(
    [
        [
            create_button(
                "➕  Aggiungi un acquisto adesso!",
                "add_purchase_now",
                "add_purchase_now",
                NEW_PURCHASE_LINK,
            )
        ]
    ]
)
