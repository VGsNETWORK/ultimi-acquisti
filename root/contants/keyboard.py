#!/usr/bin/env python3

from root.helper.wishlist import count_all_wishlist_elements_for_user
from root.contants.constant import CATEGORIES
from root.model.user import User
from typing import List
from root.model.wishlist import Wishlist
from root.model.user_rating import UserRating
from root.contants.messages import BOT_NAME
from telegram import InlineKeyboardMarkup
from root.util.util import create_button
from urllib.parse import quote
import telegram_utils.utils.logger as logger


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

ADD_TO_WISHLIST_ABORT_NO_CYCLE_KEYBOARD = InlineKeyboardMarkup(
    [
        [
            create_button(
                "☑️  Inserimento ciclico",
                "toggle_cycle_insert",
                "toggle_cycle_insert",
            )
        ],
        [
            create_button(
                "❌  Annulla",
                "cancel_add_to_wishlist_NO_DELETE",
                "cancel_add_to_wishlist_NO",
            ),
        ],
    ]
)

ADD_TO_WISHLIST_ABORT_CYCLE_KEYBOARD = InlineKeyboardMarkup(
    [
        [
            create_button(
                "✅  Inserimento ciclico",
                "toggle_cycle_insert",
                "toggle_cycle_insert",
            )
        ],
        [
            create_button(
                "❌  Annulla",
                "cancel_add_to_wishlist_NO_DELETE",
                "cancel_add_to_wishlist_NO",
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
                "❌  Annulla",
                "cancel_add_to_wishlist_NO_DELETE",
                "cancel_add_to_wishlist_NO",
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
        url = (
            "https://t.me/share/url?url=%23ultimiacquisti%20%3C"
            f"prezzo%3E%20%3CDD%2FMM%2FYY%28YY%29%3E%0A%0A%25{quote(wishlist.description)}%25"
        )
        if wishlist.link:
            url += f"%0A%0A{quote(wishlist.link)}"
        photos = " ➕ " if not wishlist.photos else "%s  " % len(wishlist.photos)
        if wishlist.photos and len(wishlist.photos) < 10:
            photos = "   %s" % photos
        if wishlist.photos:
            photo_callback: str = "view_wishlist_photo_%s_%s" % (page, wishlist.id)
        else:
            photo_callback: str = "ask_for_wishlist_photo_%s_%s" % (page, wishlist.id)
        # I hate that they are not aligned
        if wishlist.user_id == 84872221:
            btns = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
            icon = len(wishlist.photos) - 1
            icon = btns[icon]
            photos = " 0️⃣  " if not wishlist.photos else " %s  " % icon
        keyboard.append(
            [
                create_button(index, "empty_button", None),
                create_button(
                    "%s🖼" % photos,
                    photo_callback,
                    None,
                ),
                create_button(
                    "✏️",
                    "edit_wishlist_item_%s_%s_%s" % (index, page, wishlist.id),
                    None,
                ),
                create_button(
                    "🤍  🔄  🛍",
                    "convert_to_purchase_%s_%s_%s" % (index, page, wishlist.id),
                    None,
                ),
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
    if wishlists:
        wishlist = wishlists[0]
        number: int = count_all_wishlist_elements_for_user(wishlist.user_id)
        if number > 1:
            keyboard.append(
                [
                    create_button(
                        "🗑  Cancella tutti e %s gli elementi" % number,
                        "ask_delete_all_wishlist_elements_%s" % page,
                        None,
                    )
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
        [create_button("⏩  Salta passaggio", "skip_add_link_to_wishlist", None)],
        [create_button("❌  Annulla", "cancel_add_to_wishlist", None)],
    ],
)


def build_edit_wishlist_desc_keyboard(
    _id: str, page: int, index: int, text_limit_reached: bool = False
):
    keyboard = [
        [
            create_button(
                "⏩  Salta passaggio",
                "keep_current_description_%s_%s_%s" % (index, page, _id),
                None,
            )
        ],
    ]
    if text_limit_reached:
        keyboard.insert(
            0,
            [
                create_button(
                    "✅  Accetta modifica",
                    "confirm_description_mod_%s_%s_%s" % (index, page, _id),
                    None,
                ),
            ],
        )
    keyboard.append(
        [
            create_button(
                "❌  Annulla",
                "cancel_add_to_wishlist_%s_%s_%s" % (index, page, _id),
                None,
            )
        ]
    )
    return InlineKeyboardMarkup(keyboard)


def build_edit_wishlist_link_keyboard(
    _id: str, page: int, index: int, has_link: bool = True
):
    keyboard = [
        [
            create_button(
                "⏩  Salta passaggio",
                "keep_current_link_%s_%s_%s" % (index, page, _id),
                None,
            )
        ]
    ]
    if has_link:
        keyboard.append(
            [
                create_button(
                    "🗑  Rimuovi il link",
                    "remove_link_%s_%s_%s" % (index, page, _id),
                    None,
                )
            ],
        )
    keyboard.append(
        [
            create_button(
                "❌  Annulla",
                "cancel_add_to_wishlist_%s_%s_%s" % (index, page, _id),
                None,
            ),
        ]
    )
    return InlineKeyboardMarkup(keyboard)


def build_add_wishlist_category_keyboard():
    keyboard = [
        [
            create_button(
                CATEGORIES[1],
                "add_category_%s" % (1),
                None,
            ),
            create_button(
                CATEGORIES[2],
                "add_category_%s" % (2),
                None,
            ),
        ],
        [
            create_button(
                CATEGORIES[3],
                "add_category_%s" % (3),
                None,
            ),
            create_button(
                CATEGORIES[4],
                "add_category_%s" % (4),
                None,
            ),
        ],
        [
            create_button(
                CATEGORIES[0],
                "add_category_%s" % (0),
                None,
            )
        ],
        [
            create_button(
                "❌  Annulla", "cancel_add_to_wishlist", "cancel_add_to_wishlist"
            ),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_edit_wishlist_category_keyboard(
    _id: str, page: int, index: int, has_category: bool = True
):
    assigned = False
    categories = CATEGORIES
    categories = categories[1:]
    categories = zip(*(iter(categories),) * 2)
    keyboard = []
    for category in categories:
        first, second = category
        first_index, second_index = CATEGORIES.index(first), CATEGORIES.index(second)
        if has_category == first:
            if "  " in first:
                first = "✅  %s" % first.split("  ")[1]
            else:
                first = "✅  %s" % first.split(" ")[1]
            assigned = True
        elif has_category == second:
            if "  " in second:
                second = "✅  %s" % second.split("  ")[1]
            else:
                second = "✅  %s" % second.split(" ")[1]
            assigned = True
        keyboard.append(
            [
                create_button(
                    first,
                    "edit_category_%s_%s_%s_%s" % (first_index, index, page, _id),
                    None,
                ),
                create_button(
                    second,
                    "edit_category_%s_%s_%s_%s" % (second_index, index, page, _id),
                    None,
                ),
            ]
        )
    others = "✅  %s" % CATEGORIES[0].split("  ")[1] if not assigned else CATEGORIES[0]
    keyboard.append(
        [
            create_button(
                others,
                "edit_category_%s_%s_%s_%s" % (0, index, page, _id),
                None,
            )
        ]
    )
    keyboard.append(
        [
            create_button(
                "❌  Annulla",
                "cancel_add_to_wishlist_%s_%s_%s" % (index, page, _id),
                None,
            ),
        ]
    )
    return InlineKeyboardMarkup(keyboard)


def build_view_wishlist_photos_keyboard(wishlist: Wishlist, message_ids: List[int]):
    photos = wishlist.photos
    if len(photos) < 10:
        keyboard = [
            [
                create_button(
                    "➕  Aggiungi foto", "ask_for_wishlist_photo_%s" % wishlist.id, None
                )
            ]
        ]
    else:
        keyboard = []
    index = 0
    photo_groups = zip(*(iter(photos),) * 3)
    for photo_group in photo_groups:
        group = []
        for _ in photo_group:
            group.append(create_button("%s." % (index + 1), "empty_button", None))
            group.append(
                create_button(
                    "🗑", "delete_wishlist_photo_%s" % message_ids[index], None
                )
            )
            index += 1
        keyboard.append(group)
    photo_groups = zip(*(iter(photos[index:]),) * 2)
    for photo_group in photo_groups:
        group = []
        for _ in photo_group:
            group.append(create_button("%s." % (index + 1), "empty_button", None))
            group.append(
                create_button(
                    "🗑", "delete_wishlist_photo_%s" % message_ids[index], None
                )
            )
            index += 1
        keyboard.append(group)
    for _ in photos[index:]:
        keyboard.append(
            [
                create_button("%s." % (index + 1), "empty_button", None),
                create_button(
                    "🗑", "delete_wishlist_photo_%s" % message_ids[index], None
                ),
            ]
        )
        index += 1
    if len(wishlist.photos) > 1:
        keyboard.append(
            [
                create_button(
                    "🗑  Cancella tutte e %s le foto" % len(wishlist.photos),
                    "ask_delete_all_wishlist_photos",
                    None,
                )
            ]
        )
    keyboard.append(
        [create_button("↩️  Torna indietro", "go_back_from_wishlist_photos_0", None)]
    )
    return InlineKeyboardMarkup(keyboard)


def create_go_back_to_wishlist_photo_keyboard(_id: str):
    return InlineKeyboardMarkup(
        [[create_button("↩️  Torna indietro", "view_wishlist_photo_%s" % _id, None)]]
    )


def create_cancel_wishlist_photo_keyboard(
    _id: str, sended: bool = False, photos: bool = False, page: int = 0
):
    if photos:
        if sended:
            callback = "cancel_add_photo_sended_%s" % _id
        else:
            callback = "cancel_add_photo_%s" % _id
    else:
        callback = "cancel_and_go_back_%s_%s" % (_id, page)
    logger.info(callback)
    return InlineKeyboardMarkup(
        [
            [
                create_button(
                    "❌  Annulla" if not sended else "✅  Concludi inserimento",
                    callback,
                    None,
                )
            ]
        ]
    )


def create_delete_all_wishlist_items_keyboard(page: int = 0):
    return InlineKeyboardMarkup(
        [
            [
                create_button(
                    "✅  Sì",
                    "confirm_delete_all_wishlist",
                    "confirm_delete_all_wishlist",
                ),
                create_button(
                    "❌  No",
                    "abort_delete_all_wishlist_%s" % page,
                    "abort_delete_all_wishlist_%s" % page,
                ),
            ],
        ]
    )


def create_delete_all_wishlist_photos_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                create_button(
                    "✅  Sì",
                    "confirm_delete_all_wishlist_photos",
                    "confirm_delete_all_wishlist_photos",
                ),
                create_button(
                    "❌  No",
                    "abort_delete_all_wishlist_photos",
                    "abort_delete_all_wishlist_photos",
                ),
            ],
        ]
    )