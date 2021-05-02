#!/usr/bin/env python3

from root.contants.messages import BOT_NAME
from telegram import InlineKeyboardMarkup
from root.util.util import create_button


def send_command_to_group_keyboard(
    command: str, args: str = "", custom: bool = False, command_only: bool = False
):
    if command_only:
        command = f"t.me/share/url?url={command}"
    elif not custom:
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


RAITING_KEYBOARD = [
    [create_button("➡️  Salta", "skip_rating", "skip_rating")],
    [create_button("❌  Annulla", "cancel_rating", "cancel_rating")],
]


NEW_PURCHASE_FORMAT = "%23ultimiacquisti%20{}%20{}%0A%0A%25{}%25"

NEW_PURCHASE_TEMPLATE = (
    "%23ultimiacquisti%20%3Cprezzo%3E%20%3CDD%2FMM%2FYYYY%3E%0A%0A%25%3Ctitolo%3E%25"
)
NEW_PURCHASE_LINK = "https://t.me/share/url?url=%23ultimiacquisti%20%3Cprezzo%3E%20%3CDD%2FMM%2FYYYY%3E%0A%0A%25%3Ctitolo%3E%25"

ADD_PURCHASE_KEYBOARD = InlineKeyboardMarkup(
    [
        [
            create_button(
                "➕  Inserisci un nuovo acquisto",
                "add_purchase_now",
                "add_purchase_now",
                NEW_PURCHASE_LINK,
            )
        ]
    ]
)

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


def create_wrong_date_keyboard(message_id: int, modified: bool):
    discard_text = "❌  Elimina" if modified else "❌  Annulla"
    return InlineKeyboardMarkup(
        [
            [
                create_button(
                    "✅  Conferma",
                    f"confirm_purchase_{message_id}",
                    f"confirm_purchase_{message_id}",
                ),
                create_button(
                    discard_text,
                    f"remove_purchase_{message_id}",
                    f"remove_purchase_{message_id}",
                ),
            ],
        ]
    )


def build_approve_keyboard(code: str, user_id: int):
    return InlineKeyboardMarkup(
        [
            [
                create_button(
                    "✅  Sì",
                    f"approve_feedback_{code}_{user_id}",
                    f"approve_feedback_{code}_{user_id}",
                ),
                create_button(
                    "❌  No",
                    f"deny_feedback_{code}_{user_id}",
                    f"deny_feedback_{code}_{user_id}",
                ),
            ],
        ]
    )
