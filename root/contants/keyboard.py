#!/usr/bin/env python3

from root.model.user import User
from typing import List
from root.model.wishlist import Wishlist
from root.model.user_rating import UserRating
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


RATING_KEYBOARD = [
    [
        create_button("↩️  Torna indietro", "previous_rating", "previous_rating"),
        create_button("⏩  Salta passaggio", "skip_rating", "skip_rating"),
    ],
    [create_button("❌  Annulla", "rating_menu", "rating_menu")],
]


RATING_REVIEWED_KEYBOARD = InlineKeyboardMarkup(
    [
        [
            create_button(
                "✅  Ho capito",
                "delete_reviewed_rating_message",
                "delete_reviewed_rating_message",
            ),
        ]
    ]
)

NEW_PURCHASE_FORMAT = "%23ultimiacquisti%20{}%20{}%0A%0A%25{}%25"

NEW_PURCHASE_TEMPLATE = "%23ultimiacquisti%20%3Cprezzo%3E%20%3CDD%2FMM%2FYY%28YY%29%3E%0A%0A%25%3Ctitolo%3E%25"
NEW_PURCHASE_LINK = "https://t.me/share/url?url=%23ultimiacquisti%20%3Cprezzo%3E%20%3CDD%2FMM%2FYY%28YY%29%3E%0A%0A%25%3Ctitolo%3E%25"

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


SHOW_RATING_KEYBOARD = InlineKeyboardMarkup(
    [
        [
            create_button(
                "🔄  Aggiorna la recensione",
                f"start_poll",
                f"start_poll",
            )
        ],
        [create_button("↩️  Torna indietro", "rating_menu", "rating_menu")],
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


def build_pre_poll_keyboard(
    approved: UserRating, to_approve: UserRating, callback_data: str
):
    back_callback = (
        "show_bot_info" if callback_data == "rating_menu_from_info" else "cancel_rating"
    )
    if approved or to_approve:
        message = "🔄  Aggiorna la recensione"
    else:
        message = "🏁  INIZIA!"

    keyboard = []

    if approved:
        keyboard.append(
            [
                create_button(
                    "✅  Vedi la tua recensione pubblicata",
                    f"show_rating_{approved.code}",
                    f"show_rating_{approved.code}",
                )
            ]
        )

    if to_approve:
        keyboard.append(
            [
                create_button(
                    "⚖️  Vedi la tua recensione pendente",
                    f"show_rating_{to_approve.code}",
                    f"show_rating_{to_approve.code}",
                )
            ]
        )

    keyboard.append(
        [
            create_button(
                message,
                f"start_poll",
                f"start_poll",
            )
        ]
    )

    keyboard.append([create_button("↩️  Torna indietro", back_callback, back_callback)])
    return InlineKeyboardMarkup(keyboard)


def bulk_delete_keyboard(step: int):
    if step == 1:
        confirm_message = "✅  Sì"
        abort_message = "❌  NO"
    elif step == 2:
        confirm_message = "✅  Continua"
        abort_message = "❌  ANNULLA"
    elif step == 3:
        confirm_message = "🌪  CANCELLA IL MIO STORICO"
        abort_message = "❌  ANNULLA"
    else:
        return InlineKeyboardMarkup(
            [
                [
                    create_button("🆗  OK", "cancel_bulk_delete", "cancel_bulk_delete"),
                ]
            ]
        )
    if step < 3:
        return InlineKeyboardMarkup(
            [
                [
                    create_button(
                        confirm_message,
                        f"confirm_bulk_delete_{step}",
                        f"confirm_bulk_delete_{step}",
                    ),
                    create_button(
                        abort_message, "cancel_bulk_delete", "cancel_bulk_delete"
                    ),
                ]
            ]
        )
    else:
        return InlineKeyboardMarkup(
            [
                [
                    create_button(
                        confirm_message,
                        f"confirm_bulk_delete_{step}",
                        f"confirm_bulk_delete_{step}",
                    ),
                ],
                [
                    create_button(
                        abort_message, "cancel_bulk_delete", "cancel_bulk_delete"
                    ),
                ],
            ]
        )


ADDED_TO_WISHLIST_KEYBOARD = InlineKeyboardMarkup(
    [
        [
            create_button("↩️  Torna indietro", "view_wishlist_0", "view_wishlist_0"),
        ],
    ]
)

WISHLIST_KEYBOARD = InlineKeyboardMarkup(
    [
        [
            create_button("➕  Aggiungi elemento", "add_to_wishlist", "add_to_wishlist"),
        ],
        [
            create_button("↩️  Torna indietro", "cancel_rating", "cancel_rating"),
        ],
    ]
)

ADD_TO_WISHLIST_ABORT_KEYBOARD = InlineKeyboardMarkup(
    [
        [
            create_button(
                "❌  Annulla", "cancel_add_to_wishlist", "cancel_add_to_wishlist"
            ),
        ],
    ]
)

ADD_TO_WISHLIST_ABORT_TOO_LONG_KEYBOARD = InlineKeyboardMarkup(
    [
        [
            create_button(
                "✅  Accetta modifica", "keep_the_current", "keep_the_current"
            ),
        ],
        [
            create_button(
                "❌  Annulla", "cancel_add_to_wishlist", "cancel_add_to_wishlist"
            ),
        ],
    ]
)


def create_wishlist_keyboard(
    page: int,
    total_pages: int,
    wishlists: List[Wishlist],
    first_page: bool,
    last_page: bool,
):
    keyboard = [
        [
            create_button("➕  Aggiungi elemento", "add_to_wishlist", "add_to_wishlist"),
        ],
    ]
    for index, wishlist in enumerate(wishlists):
        index = "%s." % ((index) + (5 * page + 1))
        keyboard.append(
            [
                create_button(index, "empty_button", None),
                create_button(
                    "🗑", "remove_wishlist_%s_%s_%s" % (index, page, wishlist.id), None
                ),
            ]
        )
    previous_text = "🔚" if first_page else "◄"
    previous_callback = (
        "empty_button" if first_page else "view_wishlist_%s" % (page - 1)
    )
    next_text = "🔚" if last_page else "►"
    next_callback = "empty_button" if last_page else "view_wishlist_%s" % (page + 1)
    if total_pages > 1:
        keyboard.append(
            [
                create_button(previous_text, previous_callback, None),
                create_button("%s/%s" % (page + 1, total_pages), "empty_button", None),
                create_button(next_text, next_callback, None),
            ]
        )
    keyboard.append([create_button("↩️  Torna indietro", "cancel_rating", None)])
    return InlineKeyboardMarkup(keyboard)


def create_user_settings_keyboard(user: User):
    keyboard = []
    icon = "☑️" if not user.show_purchase_tips else "✅"
    message: str = f"{icon}  Suggerimenti di acquisto"
    keyboard.append(
        [
            create_button(message, "settings_toggle_tips", None),
        ]
    )
    keyboard.append([create_button("↩️  Torna indietro", "cancel_rating", None)])
    return InlineKeyboardMarkup(keyboard)


ADD_LINK_TO_WISHLIST_ITEM = InlineKeyboardMarkup(
    [
        [create_button("⏩  Salta", "skip_add_link_to_wishlist", None)],
    ]
)
