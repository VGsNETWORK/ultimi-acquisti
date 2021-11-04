#!/usr/bin/env python3

DO_NOT_LOWER_LINKS = [".youtube.", "/youtube.", "/youtu.be/", ".youtu.be/"]

CATEGORIES = [
    "📦  Altro",
    "🎮  Videogioco",
    "🗿 Collezionabile",
    "🎞  Film",
    "🖥  Elettronica",
]

MAX_WISHLIST_NAME_LENGTH = 15

PLATFORMS_REGEX = r"(?i)((^playstation)?(^ps)?(vita)?(psp)?)?((nintendo)?(switch)?([2-3]?ds)?)?((xbox)?(one)?(360)?(series)?)?"

FORMAT_ENTITIES_TYPES = [
    "strikethrough",
    "underline",
    "italic",
    "bold",
    "pre",
    "code",
    "text_link",
]

FORMAT_ENTITIES = {
    "strikethrough": "<s>%s</s>",
    "underline": "<u>%s</u>",
    "italic": "<i>%s</i>",
    "bold": "<b>%s</b>",
    "pre": "<code>%s</code>",
    "code": "<code>%s</code>",
    "text_link": '<a href="%s">%s</a>',
}
