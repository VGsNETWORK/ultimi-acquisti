#!/usr/bin/env python3

from os import environ
from root.helper import wishlist_element
from root.helper.wishlist import count_all_wishlists_for_user
from root.model.wishlist import Wishlist
from root.helper import keyboard
from root.helper.wishlist_element import (
    count_all_wishlist_elements_for_user,
    count_all_wishlist_elements_photos,
)
from root.contants.constant import CATEGORIES
from root.model.user import User
from typing import List
from root.model.wishlist_element import WishlistElement
from root.model.user_rating import UserRating
from root.contants.messages import BOT_NAME
from telegram import InlineKeyboardMarkup
from root.util.util import create_button
from urllib.parse import quote
import telegram_utils.utils.logger as logger


BOT_NAME = environ["BOT_NAME"]


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
            create_button(
                "↩️  Torna indietro",
                "view_wishlist_element_0",
                "view_wishlist_element_0",
            ),
        ],
    ]
)

WISHLIST_KEYBOARD = InlineKeyboardMarkup(
    [
        [
            create_button(
                "➕  Aggiungi elemento",
                "add_to_wishlist_element",
                "add_to_wishlist_element",
            ),
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
                "cancel_add_to_wishlist_element_NO_DELETE",
                "cancel_add_to_wishlist_element_NO",
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
                "cancel_add_to_wishlist_element_NO_DELETE",
                "cancel_add_to_wishlist_element_NO",
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
                "cancel_add_to_wishlist_element_NO_DELETE",
                "cancel_add_to_wishlist_element_NO",
            ),
        ],
    ]
)


def create_wishlist_element_keyboard(
    page: int,
    total_pages: int,
    wishlist_elements: List[WishlistElement],
    first_page: bool,
    last_page: bool,
    inc: int = 0,
    total_wishlists: int = 0,
):
    keyboard = [
        [
            create_button(
                "➕  Aggiungi elemento",
                "add_to_wishlist_element",
                "add_to_wishlist_element",
            ),
        ],
    ]
    if wishlist_elements:
        wishlist_elements = list(wishlist_elements)
        wish = wishlist_elements[-1]
        last = str(((wishlist_elements.index(wish)) + (5 * page + 1)) + inc)
        wish = wishlist_elements[0]
        first = str(0 + (5 * page + 1) + inc)
        add_space = len(last) > len(first)
    else:
        add_space = False
    for index, wishlist_element in enumerate(wishlist_elements):
        index = "%s." % ((index) + (5 * page + 1))
        if index == "%s." % last:
            space = ""
        else:
            space = "  " if add_space else ""
        url = (
            "https://t.me/share/url?url=%23ultimiacquisti%20%3C"
            f"prezzo%3E%20%3CDD%2FMM%2FYY%28YY%29%3E%0A%0A%25{quote(wishlist_element.description)}%25"
        )
        if wishlist_element.link:
            url += f"%0A%0A{quote(wishlist_element.link)}"
        photos = (
            " ➕ "
            if not wishlist_element.photos
            else "%s  " % len(wishlist_element.photos)
        )
        if wishlist_element.photos and len(wishlist_element.photos) < 10:
            photos = "   %s" % photos
        if wishlist_element.photos:
            photo_callback: str = "view_wishlist_element_photo_%s_%s" % (
                page,
                wishlist_element.id,
            )
        else:
            photo_callback: str = "ask_for_wishlist_element_photo_%s_%s" % (
                page,
                wishlist_element.id,
            )
        # I hate that they are not aligned
        if wishlist_element.user_id == 84872221:
            btns = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
            icon = len(wishlist_element.photos) - 1
            icon = btns[icon]
            photos = " 0️⃣  " if not wishlist_element.photos else " %s  " % icon
        keyboard.append(
            [
                create_button(f"{space}{index}", "empty_button", None),
                create_button(
                    "%s🖼" % photos,
                    photo_callback,
                    None,
                ),
                create_button(
                    "✏️",
                    "edit_wishlist_element_item_%s_%s_%s"
                    % (index, page, wishlist_element.id),
                    None,
                ),
                create_button(
                    "🤍  🔄  🛍",
                    "convert_to_purchase_%s_%s_%s" % (index, page, wishlist_element.id),
                    None,
                ),
                create_button(
                    "🗑",
                    "remove_wishlist_element_%s_%s_%s"
                    % (index, page, wishlist_element.id),
                    None,
                ),
            ]
        )
    previous_text = "🔚" if first_page else "◄"
    previous_callback = (
        "empty_button" if first_page else "view_wishlist_element_%s" % (page - 1)
    )
    next_text = "🔚" if last_page else "►"
    next_callback = (
        "empty_button" if last_page else "view_wishlist_element_%s" % (page + 1)
    )
    if total_pages > 1:
        keyboard.append(
            [
                create_button(previous_text, previous_callback, None),
                create_button("%s/%s" % (page + 1, total_pages), "empty_button", None),
                create_button(next_text, next_callback, None),
            ]
        )
    if wishlist_elements:
        wishlist_element = wishlist_elements[0]
        number: int = count_all_wishlist_elements_for_user(
            wishlist_element.user_id, wishlist_element.wishlist_id
        )
        if number > 1:
            wishlist_id = wishlist_element.wishlist_id
            keyboard.append(
                [
                    create_button(
                        "🗑  Cancella tutti e %s gli elementi" % number,
                        "ask_delete_all_wishlist_elements_%s_%s" % (wishlist_id, page),
                        None,
                    )
                ]
            )
    if total_wishlists > 1:
        tmessage = "🔀  Cambia lista"
        tcall = "view_other_wishlists_0"
    else:

        tmessage = "➕  Nuova lista"
        tcall = "add_new_wishlist_from_element"

    keyboard.append(
        [
            create_button("↩️  Torna indietro", "cancel_rating", None),
            create_button(tmessage, tcall, None),
        ]
    )
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
        [create_button("ℹ️  Funzioni avanzate", "show_step_2_advance", None)],
        [
            create_button("↩️  Torna indietro", "go_back_from_link", None),
            create_button(
                "⏩  Salta passaggio", "skip_add_link_to_wishlist_element", None
            ),
        ],
        [create_button("❌  Annulla", "cancel_add_to_wishlist_element", None)],
    ],
)


def build_edit_wishlist_element_desc_keyboard(
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
                "cancel_add_to_wishlist_element_%s_%s_%s" % (index, page, _id),
                None,
            )
        ]
    )
    return InlineKeyboardMarkup(keyboard)


def build_edit_wishlist_element_link_keyboard(
    _id: str, page: int, index: int, has_link: bool = True
):
    keyboard = [
        [
            create_button(
                "↩️  Torna indietro",
                "go_back_from_link_%s_%s_%s" % (index, page, _id),
                None,
            ),
            create_button(
                "⏩  Salta passaggio",
                "keep_current_link_%s_%s_%s" % (index, page, _id),
                None,
            ),
        ]
    ]
    keyboard.insert(
        0, [create_button("ℹ️  Funzioni avanzate", "show_step_2_advance", None)]
    )
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
                "cancel_add_to_wishlist_element_%s_%s_%s" % (index, page, _id),
                None,
            ),
        ]
    )
    return InlineKeyboardMarkup(keyboard)


def build_add_wishlist_element_category_keyboard():
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
        [create_button("↩️  Torna indietro", "go_back_from_category", None)],
        [
            create_button(
                "❌  Annulla",
                "cancel_add_to_wishlist_element",
                "cancel_add_to_wishlist_element",
            ),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_edit_wishlist_element_category_keyboard(
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
                "↩️  Torna indietro",
                "go_back_from_category_%s_%s_%s" % (index, page, _id),
                None,
            )
        ]
    )
    keyboard.append(
        [
            create_button(
                "❌  Annulla",
                "cancel_add_to_wishlist_element_%s_%s_%s" % (index, page, _id),
                None,
            ),
        ]
    )
    return InlineKeyboardMarkup(keyboard)


def build_view_wishlist_element_photos_keyboard(
    wishlist_element: WishlistElement, message_ids: List[int]
):
    photos = wishlist_element.photos
    if len(photos) < 10:
        keyboard = [
            [
                create_button(
                    "➕  Aggiungi foto",
                    "ask_for_wishlist_element_photo_%s" % wishlist_element.id,
                    None,
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
                    "🗑", "delete_wishlist_element_photo_%s" % message_ids[index], None
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
                    "🗑", "delete_wishlist_element_photo_%s" % message_ids[index], None
                )
            )
            index += 1
        keyboard.append(group)
    for _ in photos[index:]:
        keyboard.append(
            [
                create_button("%s." % (index + 1), "empty_button", None),
                create_button(
                    "🗑", "delete_wishlist_element_photo_%s" % message_ids[index], None
                ),
            ]
        )
        index += 1
    if len(wishlist_element.photos) > 1:
        keyboard.append(
            [
                create_button(
                    "🗑  Cancella tutte e %s le foto" % len(wishlist_element.photos),
                    "ask_delete_all_wishlist_element_photos",
                    None,
                )
            ]
        )
    keyboard.append(
        [
            create_button(
                "↩️  Torna indietro", "go_back_from_wishlist_element_photos_0", None
            )
        ]
    )
    return InlineKeyboardMarkup(keyboard)


def create_go_back_to_wishlist_element_photo_keyboard(_id: str):
    return InlineKeyboardMarkup(
        [
            [
                create_button(
                    "↩️  Torna indietro", "view_wishlist_element_photo_%s" % _id, None
                )
            ]
        ]
    )


def create_cancel_wishlist_element_photo_keyboard(
    _id: str,
    sended: bool = False,
    photos: bool = False,
    page: int = 0,
    download_supported: bool = False,
    link: str = "",
):
    if photos:
        if sended:
            callback = "cancel_add_photo_sended_%s" % _id
        else:
            callback = "cancel_add_photo_%s" % _id
    else:
        callback = "cancel_and_go_back_%s_%s" % (_id, page)
    logger.info(callback)
    keyboard = [
        [
            create_button(
                "❌  Annulla" if not sended else "✅  Concludi inserimento",
                callback,
                None,
            )
        ]
    ]
    if download_supported:
        keyboard.insert(
            0,
            [
                create_button(
                    "⬇️  Scarica dal web",
                    "auto_download_pictures_%s" % _id,
                    None,
                )
            ],
        )
    else:
        logger.info("This is the %s" % link)
        if link:
            if link != "" or link != "None":
                keyboard.insert(
                    0,
                    [
                        create_button(
                            "⚠️  Domini web supportati",
                            "show_supported_link",
                            "show_supported_link",
                        )
                    ],
                )
    return InlineKeyboardMarkup(keyboard)


def create_delete_all_wishlist_element_items_keyboard(
    page: int = 0, from_wishlist=False, wishlist_id=""
):
    if from_wishlist:
        yes_callback = "confirm_delete_wishlist_list_%s" % wishlist_id
        no_callback = "view_other_wishlists_%s" % page
    else:
        yes_callback = "confirm_delete_all_wishlist_element_%s" % wishlist_id
        no_callback = "abort_delete_all_wishlist_element_%s" % page

    return InlineKeyboardMarkup(
        [
            [
                create_button(
                    "✅  Sì",
                    yes_callback,
                    yes_callback,
                ),
                create_button("❌  No", no_callback, no_callback),
            ],
        ]
    )


def create_delete_all_wishlist_element_photos_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                create_button(
                    "✅  Sì",
                    "confirm_delete_all_wishlist_element_photos",
                    "confirm_delete_all_wishlist_element_photos",
                ),
                create_button(
                    "❌  No",
                    "abort_delete_all_wishlist_element_photos",
                    "abort_delete_all_wishlist_element_photos",
                ),
            ],
        ]
    )


def create_other_wishlist_keyboard(
    page: int,
    total_pages: int,
    wishlists: List[Wishlist],
    first_page: bool,
    last_page: bool,
    inc: int,
    total_lists: int,
    current_wishlist: str,
    user_id: int,
):
    if total_lists < 10:
        keyboard = [
            [
                create_button(
                    "➕  Crea nuova lista",
                    "add_new_wishlist",
                    "add_new_wishlist",
                ),
            ],
        ]
    else:
        keyboard = []
    if wishlists:
        wishlists = list(wishlists)
        wish = wishlists[-1]
        last = str(((wishlists.index(wish)) + (5 * page + 1)) + inc)
        wish = wishlists[0]
        first = str(0 + (5 * page + 1) + inc)
        add_space = len(last) > len(first)
    else:
        add_space = False
    for index, wishlist in enumerate(wishlists):
        photos: int = count_all_wishlist_elements_photos(user_id, str(wishlist.id))
        elements: int = count_all_wishlist_elements_for_user(user_id, str(wishlist.id))
        # I hate that they are not aligned
        if not str(wishlist.id) == current_wishlist:
            title = wishlist.title
        else:
            title = "✅    %s" % (wishlist.title)
        if photos:
            title += f" │ {elements} 🗂  {photos} 🖼"
        elif elements:
            title += f" │ {elements} 🗂"
        else:
            title += "  (vuota)"
        line = [
            [
                create_button(
                    title, "change_current_wishlist_%s" % str(wishlist.id), None
                )
            ]
        ]

        if not wishlist.default_wishlist:
            line.append(
                [
                    create_button(
                        "✏️", "edit_wishlist_name_%s" % str(wishlist.id), None
                    ),
                    create_button(
                        "🗑",
                        "ask_delete_wishlist_and_elements_%s_%s" % (wishlist.id, page),
                        None,
                    ),
                ]
            )
        else:
            line.append(
                [
                    create_button(
                        "✏️", "edit_wishlist_name_%s" % str(wishlist.id), None
                    ),
                ]
            )
        keyboard.append(line[0])
        if len(line) > 1:
            keyboard.append(line[1])
    previous_text = "🔚" if first_page else "◄"
    previous_callback = (
        "empty_button" if first_page else "view_other_wishlists_%s" % (page - 1)
    )
    next_text = "🔚" if last_page else "►"
    next_callback = (
        "empty_button" if last_page else "view_other_wishlists_%s" % (page + 1)
    )
    return InlineKeyboardMarkup(keyboard)


def add_new_wishlist_keyboard(from_element: bool):
    # TODO: fix
    callback = (
        "cancel_add_to_wishlist" if not from_element else "cancel_add_to_wishlist"
    )
    return InlineKeyboardMarkup(
        [
            [
                create_button(
                    "❌  Annulla",
                    callback,
                    callback,
                ),
            ]
        ]
    )


def edit_wishlist_name_keyboard(from_element: bool):
    callback = "cancel_edit_wishlist"
    return InlineKeyboardMarkup(
        [
            [
                create_button(
                    "❌  Annulla",
                    callback,
                    callback,
                ),
            ]
        ]
    )


def add_new_wishlist_too_long_keyboard(from_element: bool):
    # TODO: fix
    callback = (
        "cancel_add_to_wishlist" if not from_element else "cancel_add_to_wishlist"
    )
    return InlineKeyboardMarkup(
        [
            [
                create_button(
                    "✅  Accetta modifica", "keep_the_current", "keep_the_current"
                ),
            ],
            [
                create_button(
                    "❌  Annulla",
                    callback,
                    callback,
                ),
            ],
        ]
    )


def edit_wishlist_name_too_long_keyboard(from_element: bool):
    # TODO: fix
    callback = "cancel_edit_wishlist"
    return InlineKeyboardMarkup(
        [
            [
                create_button("✅  Accetta modifica", "confirm_edit", "confirm_edit"),
            ],
            [
                create_button(
                    "❌  Annulla",
                    callback,
                    callback,
                ),
            ],
        ]
    )


AD_KEYBOARD_ONE = InlineKeyboardMarkup(
    [
        [
            create_button(
                "ℹ️  Maggiori informazioni",
                "empty_button",
                "empty_button",
                url=f"t.me/{BOT_NAME}?start=how_to",
            )
        ]
    ]
)

AD_KEYBOARD_TWO = InlineKeyboardMarkup(
    [
        [
            create_button(
                "ℹ️  Maggiori informazioni",
                "empty_button",
                "empty_button",
                url=f"t.me/{BOT_NAME}?start=wishlist",
            )
        ]
    ]
)


AD_KEYBOARD_THREE = InlineKeyboardMarkup(
    [
        [
            create_button(
                "ℹ️  Maggiori informazioni",
                "empty_button",
                "empty_button",
                url=f"t.me/{BOT_NAME}?start=command_list_3",
            )
        ]
    ]
)

AD_KEYBOARD_FOUR = InlineKeyboardMarkup(
    [
        [
            create_button(
                "ℹ️  Maggiori informazioni",
                "empty_button",
                "empty_button",
                url=f"t.me/{BOT_NAME}?start=command_list_6",
            )
        ],
    ]
)

ADS_KEYBOARDS = [
    AD_KEYBOARD_ONE,
    AD_KEYBOARD_TWO,
    AD_KEYBOARD_THREE,
    AD_KEYBOARD_FOUR,
]
