#!/usr/bin/env python3

from difflib import SequenceMatcher
from operator import add, contains
from os import environ
from re import I, S, sub
import re

from telegram import callbackquery
from root.handlers.generic import de_html
from root.contants.message_timeout import THIRTY_MINUTES

from telegram.bot import Bot
from root.helper.process_helper import find_process, stop_process, create_process
from time import sleep
from root.util.util import format_date, format_price, format_time
from typing import List
from root.model.tracked_link import TrackedLink
from root.helper.subscriber_helper import find_subscriber
from root.model.subscriber import Subscriber
from root.helper.tracked_link_helper import (
    find_link_by_code,
    find_link_by_id,
    remove_tracked_subscriber,
    update_or_create_scraped_link,
    update_scraped_link_information,
)

import telegram_utils.helper.redis as redis_helper
import telegram_utils.utils.logger as logger
from root.handlers.handlers import extractor
from root.contants.keyboard import (
    build_new_link_keyboard,
    build_new_link_keyboard_added,
    view_wishlist_element_links_keyboard,
)
from root.contants.messages import (
    ADD_NEW_LINK_MESSAGE,
    ADD_NEW_LINK_MESSAGE_NUMBER_OF_NEW_LINK,
    ADD_NEW_LINK_MESSAGE_NUMBER_OF_NEW_PHOTOS,
    PREMIUM_DEALS_MESSAGES,
    PRICE_MESSAGE_POPUP,
    PRICE_MESSAGE_POPUP_NO_VARIATION,
    PRODUCT_DEAL,
    PRODUCT_TYPE,
    SUPPORTED_LINKS_MESSAGE,
    TRACKED_LINK_EXPLANATION,
    WISHLIST_HEADER,
    WISHLIST_LINK_LEGEND_APPEND,
    WISHLIST_LINK_LEGEND_APPEND_VARIATION,
    WISHLIST_LINK_LIMIT_REACHED,
)
from root.helper import wishlist_element
from root.helper.user_helper import get_current_wishlist_id
from root.helper.wishlist import find_wishlist_by_id
from root.helper.wishlist_element import (
    find_next_wishlist_element,
    find_previous_wishlist_element,
    find_wishlist_element_by_id,
)
from root.model.user import User
from root.model.wishlist import Wishlist
from root.model.wishlist_element import WishlistElement
from telegram.chat import Chat
from telegram.error import BadRequest
from telegram.ext import ConversationHandler
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.message import Message
from telegram.update import Update

APPEND_LINK = range(1)
MAX_LINK_LENGTH = 27
MAX_LINKS_NUMBER = 10


def show_price_popup(update: Update, context: CallbackContext):
    logger.info("SHOW PRICE")
    user: User = update.effective_user
    tracked_list_id: str = update.callback_query.data.split("_")[-2]
    wishlist_element_id: str = update.callback_query.data.split("_")[-1]
    tracked_link: TrackedLink = find_link_by_id(tracked_list_id)
    subscriber: Subscriber = find_subscriber(user.id, tracked_link.code)
    wishlist_element: WishlistElement = find_wishlist_element_by_id(wishlist_element_id)
    try:
        if tracked_link.price < subscriber.lowest_price:
            sign = "📉"
        elif tracked_link.price > subscriber.lowest_price:
            sign = "📈"
        else:
            sign = "➖"
    except ValueError:
        sign = "➖"
    title = wishlist_element.description
    if len(title) > 20:
        title = "%s..." % title[:17]
    else:
        title = title
    title = "%s  –  %s" % (title, extractor.get_match(tracked_link.link))
    extra_price = extractor.get_shipment_cost(
        tracked_link.price, tracked_link.link, True
    )
    if extra_price:
        extra_price = "%s" % extra_price
    extra_lowest = extractor.get_shipment_cost(
        subscriber.lowest_price, tracked_link.link, True
    )
    if extra_lowest:
        extra_lowest = " + %s" % extra_lowest
    extra = extractor.show_extra_info(tracked_link)
    if tracked_link.price > 0:
        price = "%s €" % format_price(tracked_link.price)
    else:
        price = "N/D"
    lowest_price = format_price(subscriber.lowest_price)
    if float(subscriber.lowest_price) > 0:
        lowest_price = "%s €" % lowest_price
    if not subscriber.never_updated:
        message = PRICE_MESSAGE_POPUP % (
            title.upper(),
            price,
            sign,
            extra,
            "%s%s" % (lowest_price, extra_lowest),
        )
    else:
        message = PRICE_MESSAGE_POPUP_NO_VARIATION % (
            title.upper(),
            price,
            "\n%s" % extra,
        )
    context.bot.answer_callback_query(
        update.callback_query.id, show_alert=True, text=message
    )


def delete_wishlist_element_link(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    message_id: int = message.message_id
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    if update.callback_query:
        data = update.callback_query.data
        logger.info("THIS IS THE DATA: [%s]" % data)
        wishlist_element_id = data.split("_")[-1]
        page = data.split("_")[-2]
        index = int(data.split("_")[-3])
        wishlist_element: WishlistElement = find_wishlist_element_by_id(
            wishlist_element_id
        )
        links = wishlist_element.links
        links.reverse()
        link = links[index + 1]
        if extractor.is_supported(link):
            logger.info("LINK IS SUPPORTED")
            logger.info(link)
            remove_tracked_subscriber(extractor.extract_code(link), user.id)
        else:
            logger.info("LINK IS NOT SUPPORTED")
        links.pop(index + 1)
        links.reverse()
        wishlist_element.links = links
        wishlist_element.save()
        view_wishlist_element_links(update, context)
    return


def update_list(update: Update, context: CallbackContext, show_update: bool = False):
    user: User = update.effective_user
    if not show_update:
        logger.info("HIDING THE SHOW_UPDATE")
        redis_helper.save("%s_%s_on_list" % (user.id, user.id), "1")
        logger.info("SHOWING THE LINKS")
        view_wishlist_element_links(update, context, show_update=show_update)
        create_process(
            "update_link_list_%s" % (user.id),
            update_list,
            (
                update,
                context,
                True,
            ),
        )
    else:
        logger.info("SHOWING THE SHOW_UPDATE")
        on_list = redis_helper.retrieve("%s_%s_on_list" % (user.id, user.id))
        if on_list:
            on_list = on_list.decode()
            if on_list == "1":
                sleep(THIRTY_MINUTES)
                redis_helper.save("%s_%s_on_list" % (user.id, user.id), "1")
                logger.info("SHOWING THE LINKS")
                view_wishlist_element_links(
                    update, context, show_update=show_update, scrape=False
                )
            else:
                logger.info("skipping for not in link message...")
                return


def view_wishlist_element_links(
    update: Update,
    context: CallbackContext,
    append: str = None,
    show_update: bool = False,
    scrape: bool = True,
):
    logger.info("show_update: %s" % show_update)
    message: Message = update.effective_message
    message_id: int = message.message_id
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    if find_process("update_link_list_%s" % (user.id)):
        show_update = False
        scrape = False
    redis_helper.save("%s_%s_on_list" % (user.id, user.id), "1")
    if update.callback_query:
        data = update.callback_query.data
        if "view_wishlist_link_element" in data:
            scrape = True
        wishlist_element_id = data.split("_")[-1]
        page = data.split("_")[-2]
    else:
        info = redis_helper.retrieve(
            "%s_%s_new_link_message" % (user.id, user.id)
        ).decode()
        page = info.split("_")[-2]
        message_id = info.split("_")[-4]
        wishlist_element_id = info.split("_")[-3]
    wishlist_element: WishlistElement = find_wishlist_element_by_id(wishlist_element_id)
    previous_element: WishlistElement = find_previous_wishlist_element(
        user.id, wishlist_element
    )
    next_element: WishlistElement = find_next_wishlist_element(
        user.id, wishlist_element
    )
    links = []
    tracked_links = []
    tc = []
    for link in wishlist_element.links:
        if extractor.is_supported(link):
            code: str = extractor.extract_code(link)
            logger.info("finding by code [%s]" % code)
            tracked_link: TrackedLink = find_link_by_code(code)
            tracked_links.append(tracked_link)
        else:
            links.insert(0, link)
    logger.info(tracked_links)
    tracked_links = [t for t in tracked_links if t != None]
    tracked_links.sort(
        key=lambda link: (
            link.price + extractor.get_shipment_cost(link.price, link.link)
        ),
        reverse=True,
    )
    for link in tracked_links:
        logger.info("checking price for %s" % link.link)
        if link.price > 0:
            tc.append(link)
        else:
            tc.insert(0, link)
    [logger.info(link.link) for link in tc]
    tracked_links = tc
    [links.insert(0, link.link) for link in tracked_links]
    links.reverse()
    wishlist_element.links = links
    wishlist_element.save()
    wishlist: Wishlist = find_wishlist_by_id(wishlist_element.wishlist_id)
    ####
    links = wishlist_element.links
    title = f"{wishlist.title.upper()}  –  "
    message = WISHLIST_HEADER % title
    if links:
        message += f"Hai aggiunto  <code>{len(links)}</code>  link per <b>{wishlist_element.description}</b>.\n"
        is_tracked = next(
            (True for link in links if extractor.is_supported(link)), False
        )
        if is_tracked:
            message += TRACKED_LINK_EXPLANATION
        wishlist_element.links.reverse()
        if len(wishlist_element.links) == 10 or is_tracked:
            leading_space = " "
            spaces_before_medal = ""
        else:
            leading_space = ""
            spaces_before_medal = ""
        medals = ["🥇", "🥈", "🥉"]
        for index, wishlist_link in enumerate(wishlist_element.links):
            if extractor.is_supported(wishlist_link):
                tracked_link: TrackedLink = find_link_by_code(
                    extractor.extract_code(wishlist_link)
                )
                logger.info("IS DIGITAL [%s]" % tracked_link.digital)
                if tracked_link.deals_end:
                    if tracked_link.deals_percentage:
                        deal = int(tracked_link.deals_percentage)
                    else:
                        deal = 0
                    logger.info(
                        "THE PRODUCT IS PREMIUM [%s]" % tracked_link.included_in_premium
                    )
                    if not tracked_link.included_in_premium:
                        deal_date = PRODUCT_DEAL % (
                            deal,
                            format_time(tracked_link.deals_end),
                            format_date(tracked_link.deals_end, timezone=True),
                        )
                    else:
                        if tracked_link.store in PREMIUM_DEALS_MESSAGES:
                            deal_date = PREMIUM_DEALS_MESSAGES[tracked_link.store]
                            if deal_date:
                                logger.info(f"*** {tracked_link.premium_type} ***")
                                if tracked_link.premium_type in deal_date:
                                    deal_date = deal_date[tracked_link.premium_type]
                                    deal_date = deal_date % (
                                        format_time(tracked_link.deals_end),
                                        format_date(
                                            tracked_link.deals_end, timezone=True
                                        ),
                                    )
                                else:
                                    deal_date = PRODUCT_DEAL % (
                                        deal,
                                        format_time(tracked_link.deals_end),
                                        format_date(
                                            tracked_link.deals_end, timezone=True
                                        ),
                                    )
                            else:
                                deal_date = PRODUCT_DEAL % (
                                    deal,
                                    format_time(tracked_link.deals_end),
                                    format_date(tracked_link.deals_end, timezone=True),
                                )
                        else:
                            deal_date = PRODUCT_DEAL % (
                                deal,
                                format_time(tracked_link.deals_end),
                                format_date(tracked_link.deals_end, timezone=True),
                            )
                else:
                    deal_date = "<code>    </code>"
                if tracked_link.platform == "MISSING":
                    tracked = f"  (💹)"
                else:
                    if tracked_link.digital:
                        tracked = f"  (💹)\n<i>{deal_date}{tracked_link.platform} ({PRODUCT_TYPE[tracked_link.digital]})</i>"
                    else:
                        tracked = f"  (💹)\n<i>{deal_date}{tracked_link.platform} ({PRODUCT_TYPE[False]})</i>"
            else:
                tracked = ""
            if index == 9:
                spaces_before_medal = ""
            if len(wishlist_link) > MAX_LINK_LENGTH:
                wishlist_link = '<a href="%s">%s...</a>' % (
                    wishlist_link,
                    wishlist_link[:MAX_LINK_LENGTH],
                )
            if not tracked:
                i = "<code>%s<b>%s.</b> </code>" % (leading_space, (index + 1))
            else:
                if index > 2:
                    if is_tracked:
                        i = "<code>%s<b>%s.</b> </code>" % (leading_space, (index + 1))
                else:
                    i = "<code> %s </code>" % medals[index]
            if index == 0:
                if len(wishlist_element.links) > 1:
                    message += f"\n{spaces_before_medal}{i}{wishlist_link}{tracked}"
                else:
                    message += f"\n{spaces_before_medal}{i}{wishlist_link}{tracked}"
            elif index == len(wishlist_element.links) - 1:
                message += f"\n\n{spaces_before_medal}{i}{wishlist_link}{tracked}"
            else:
                message += f"\n\n{spaces_before_medal}{i}{wishlist_link}{tracked}"
    else:
        message += (
            f"Qui puoi aggiungere dei link per <b>{wishlist_element.description}</b>."
        )
    if len(links) == MAX_LINKS_NUMBER:
        message += WISHLIST_LINK_LIMIT_REACHED
    subscribers: List[Subscriber] = []
    tracked_links: List[TrackedLink] = []
    deals: List[str] = []
    new_prices = []
    show_legend = False
    never_updated = False
    for link in wishlist_element.links:
        if extractor.is_supported(link):
            logger.info("SUPPORTED LINK")
            show_legend = True
            subscriber: Subscriber = find_subscriber(
                user.id, extractor.extract_code(link)
            )
            if not subscriber.never_updated:
                never_updated = True
            tracked_link: TrackedLink = find_link_by_code(extractor.extract_code(link))
            if subscriber and tracked_link:
                try:
                    if scrape:
                        logger.info("SCRAPING IT")
                        if "www." in link:
                            link = re.sub("www\.", "", link)
                        product = extractor.parse_url(link)
                        new_price = float(product["price"])
                        if find_link_by_code(product["code"]):
                            update_scraped_link_information(product)
                        else:
                            update_or_create_scraped_link(product)
                        logger.info("FINDING TRACKED_LINK")
                        tracked_link: TrackedLink = find_link_by_code(product["code"])
                    else:
                        logger.info("DOING NOTHING")
                        new_price = tracked_link.price
                    logger.info("ADDING (IF NEEDED) SHIPPING")
                    tracked_link.price += extractor.get_shipment_cost(
                        tracked_link.price, tracked_link.link
                    )
                    new_price += extractor.get_shipment_cost(
                        tracked_link.price, tracked_link.link
                    )
                    subscriber.lowest_price += extractor.get_shipment_cost(
                        tracked_link.price, tracked_link.link
                    )
                    logger.info("CHECKING PRICES")
                    logger.info("%s - %s" % (new_price, subscriber.lowest_price))
                    if new_price < subscriber.lowest_price:
                        deals.append("📉")
                        new_prices.append(new_price)
                    elif new_price > subscriber.lowest_price:
                        deals.append("📈")
                    else:
                        deals.append("➖")
                except ValueError:
                    logger.info("VALUE ERROR")
                    new_prices.append(0.00)
                    pass
                logger.info("REMOVING (IF NEEDED) SHIPPING")
                tracked_link.price -= extractor.get_shipment_cost(
                    tracked_link.price, tracked_link.link
                )
                new_price -= extractor.get_shipment_cost(
                    tracked_link.price, tracked_link.link
                )
                subscriber.lowest_price -= extractor.get_shipment_cost(
                    tracked_link.price, tracked_link.link
                )
                subscribers.append(subscriber)
                tracked_links.append(tracked_link)
            else:
                deals.append("➖")
                new_prices.append(0.00)
                subscribers.append("do_not_show")
                tracked_links.append("do_not_show")
        else:
            deals.append("➖")
            new_prices.append(0.00)
            subscribers.append("do_not_show")
            tracked_links.append("do_not_show")
    logger.info(
        "%s - %s - %s"
        % (
            len(wishlist_element.links),
            len(subscribers),
            len(tracked_links),
        )
    )
    logger.info("getting keyboard")
    keyboard: InlineKeyboardMarkup = view_wishlist_element_links_keyboard(
        wishlist_element_id,
        page,
        wishlist_element.links,
        subscribers,
        tracked_links,
        deals,
        show_update,
        previous_element,
        next_element,
    )
    logger.info("got the keyboard")
    for index, subscriber in enumerate(subscribers):
        logger.info("index %s" % index)
        if deals[index] == "📉":
            subscriber.lowest_price = new_prices[index]
            # subscriber.save()
    if show_legend:
        message += WISHLIST_LINK_LEGEND_APPEND
        if never_updated:
            message += WISHLIST_LINK_LEGEND_APPEND_VARIATION
    try:
        logger.info("editing message")
        bot = Bot(environ["TOKEN"])
        if update.callback_query:
            data = update.callback_query.data
            if not "view_wishlist_link_element" in data:
                bot.edit_message_text(
                    message_id=message_id,
                    chat_id=chat.id,
                    text=message,
                    reply_markup=keyboard,
                    disable_web_page_preview=True,
                    parse_mode="HTML",
                )
            else:
                update.callback_query.data = str(data).replace(
                    "view_wishlist_link_element", "ignore_update"
                )
        else:
            bot.edit_message_text(
                message_id=message_id,
                chat_id=chat.id,
                text=message,
                reply_markup=keyboard,
                disable_web_page_preview=True,
                parse_mode="HTML",
            )
        if scrape:
            update_list(update, context, False)
    except BadRequest as e:
        logger.error("UNABLE TO EDIT MESSAGE")
        logger.error(e)
        pass


def ask_for_new_link(update: Update, context: CallbackContext):
    logger.info("ASKING FOR NEW LINK")
    message: Message = update.effective_message
    message_id: int = message.message_id
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    redis_helper.save("%s_%s_on_list" % (user.id, user.id), "0")
    if update.callback_query:
        logger.info("FROM BUTTON")
        data = update.callback_query.data
        wishlist_element_id = data.split("_")[-1]
        page = data.split("_")[-2]
        wishlist_element: WishlistElement = find_wishlist_element_by_id(
            wishlist_element_id
        )
        from_wishlist = len(wishlist_element.links) == 0
        info: str = "%s_%s_%s_%s" % (
            message_id,
            wishlist_element_id,
            page,
            from_wishlist,
        )
        redis_helper.save("%s_%s_new_link_message" % (user.id, user.id), str(info))
        redis_helper.save("%s_%s_duplicated_links" % (user.id, user.id), str([]))
        wishlist_id = get_current_wishlist_id(user.id)
        wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
        title = f"{wishlist.title.upper()}  –  "
        if wishlist_element.links:
            append = ADD_NEW_LINK_MESSAGE_NUMBER_OF_NEW_LINK % (
                len(wishlist_element.links),
                MAX_LINKS_NUMBER,
            )
        else:
            append = ""
        wishlist_element.links.reverse()
        for index, wishlist_link in enumerate(wishlist_element.links):
            if len(wishlist_link) > MAX_LINK_LENGTH:
                wishlist_link = '<a href="%s">%s...</a>' % (
                    wishlist_link,
                    wishlist_link[:MAX_LINK_LENGTH],
                )
            if index == 0:
                if len(wishlist_element.links) > 1:
                    append += f"  ├─  {wishlist_link}"
                else:
                    append += f"  └─  {wishlist_link}"
            elif index == len(wishlist_element.links) - 1:
                append += f"\n  └─  {wishlist_link}"
            else:
                append += f"\n  ├─  {wishlist_link}"
        if wishlist_element.links:
            append += "\n\n"
        message = ADD_NEW_LINK_MESSAGE % (title, append, wishlist_element.description)
        context.bot.edit_message_text(
            message_id=message_id,
            chat_id=chat.id,
            text=message,
            reply_markup=build_new_link_keyboard(page, wishlist_element_id),
            disable_web_page_preview=True,
            parse_mode="HTML",
        )
        return APPEND_LINK


def append_link(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    message_id: int = message.message_id
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    wishlist_link: str = message.text
    wishlist_link = re.sub(r".*//", "", wishlist_link)
    logger.info(wishlist_link)
    context.bot.delete_message(message_id=message_id, chat_id=chat.id)
    info = redis_helper.retrieve("%s_%s_new_link_message" % (user.id, user.id)).decode()
    duplicated_links = eval(
        redis_helper.retrieve("%s_%s_duplicated_links" % (user.id, user.id)).decode()
    )
    # number ofhttps://www.gamestop.it/PS5/Games/131445/demons-soulsview links
    wishlist_element_id = info.split("_")[-3]
    message_id = info.split("_")[-4]
    page = info.split("_")[-2]
    wishlist_element: WishlistElement = find_wishlist_element_by_id(wishlist_element_id)
    is_present = False
    for link in wishlist_element.links:
        if not is_present:
            is_present = SequenceMatcher(None, wishlist_link, link).ratio() > 0.9
            duplicated_type = "DUPLICATO"
    if not is_present:
        is_present = extractor.domain_duplicated(wishlist_link, wishlist_element.links)
        duplicated_type = "DOMINIO WEB DUPLICATO"
    if not is_present:
        is_present = find_subscriber(user.id, extractor.extract_code(wishlist_link))
        duplicated_type = "DUPLICATO IN UN ALTRO ELEMENTO"
    if is_present:
        if len(wishlist_link) > MAX_LINK_LENGTH:
            wishlist_link = '<a href="%s">%s...</a>' % (
                wishlist_link,
                wishlist_link[:MAX_LINK_LENGTH],
            )
        duplicated_link = "<s>%s</s>     🚫 <b>%s</b>" % (wishlist_link, duplicated_type)
        if len(duplicated_links) == 10:
            duplicated_links.pop()
        duplicated_links.insert(0, duplicated_link)
        redis_helper.save(
            "%s_%s_duplicated_links" % (user.id, user.id), str(duplicated_links)
        )
        pictures = extractor.load_url(wishlist_link)
    else:
        logger.info(wishlist_link)
        pictures = extractor.load_url(wishlist_link)
        try:
            logger.info("parsing URL")
            wishlist_link = re.sub(r".*//", "", wishlist_link)
            if "www." in wishlist_link:
                wishlist_link = re.sub("www\.", "", wishlist_link)
            product = extractor.parse_url(wishlist_link)
            extractor.add_subscriber(wishlist_link, user.id, product)
        except ValueError as e:
            logger.error(e)
        number_of_photos = len(wishlist_element.photos)
        if not number_of_photos == 10:
            photos_left = 10 - number_of_photos
            pictures = pictures[:photos_left]
            [wishlist_element.photos.append(pic) for pic in pictures]
        duplicated_link = None
        wishlist_element.links.append(wishlist_link)
        wishlist_element.save()
        if len(wishlist_element.links) == MAX_LINKS_NUMBER:
            return complete_operation(update, context)
    wishlist_id = get_current_wishlist_id(user.id)
    wishlist: Wishlist = find_wishlist_by_id(wishlist_id)
    title = f"{wishlist.title.upper()}  –  "
    if wishlist_element.links or duplicated_links:
        append = ADD_NEW_LINK_MESSAGE_NUMBER_OF_NEW_LINK % (
            len(wishlist_element.links),
            MAX_LINKS_NUMBER,
        )
    else:
        append = ""
    wishlist_element.links.reverse()
    links = wishlist_element.links
    for index, duplicated_link in enumerate(duplicated_links):
        links.insert(index, duplicated_link)
    for index, wishlist_link in enumerate(links):
        if len(wishlist_link) > MAX_LINK_LENGTH:
            if not "DUPLICATO" in wishlist_link:
                wishlist_link = '<a href="%s">%s...</a>' % (
                    wishlist_link,
                    wishlist_link[:MAX_LINK_LENGTH],
                )
        if index == 0:
            if len(wishlist_element.links) > 1:
                append += f"  ├─  {wishlist_link}"
            else:
                append += f"  └─  {wishlist_link}"
        elif index == len(wishlist_element.links) - 1:
            append += f"\n  └─  {wishlist_link}"
        else:
            append += f"\n  ├─  {wishlist_link}"
    if wishlist_element.links:
        append += "\n\n"
    message = ADD_NEW_LINK_MESSAGE % (title, append, wishlist_element.description)
    keyboard = build_new_link_keyboard_added(page, wishlist_element_id)
    if pictures and number_of_photos < 10:
        message += ADD_NEW_LINK_MESSAGE_NUMBER_OF_NEW_PHOTOS % (
            len(pictures),
            "e" if len(pictures) > 1 else "a",
        )
    try:
        context.bot.edit_message_text(
            message_id=message_id,
            chat_id=chat.id,
            text=message,
            reply_markup=keyboard,
            disable_web_page_preview=True,
            parse_mode="HTML",
        )
    except BadRequest:
        return APPEND_LINK
    return APPEND_LINK


def complete_operation(update: Update, context: CallbackContext):
    view_wishlist_element_links(update, context)
    return ConversationHandler.END


def show_step_two_toast(update: Update, context: CallbackContext):
    context.bot.answer_callback_query(
        update.callback_query.id, text=SUPPORTED_LINKS_MESSAGE, show_alert=True
    )
    return APPEND_LINK


def cancel_link_append(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    message_id: int = message.message_id
    chat: Chat = update.effective_chat
    user: User = update.effective_user
    info = redis_helper.retrieve("%s_%s_new_link_message" % (user.id, user.id)).decode()
    page = info.split("_")[-2]
    from_wishlist = eval(info.split("_")[-1])
    wishlist_element_id = info.split("_")[-3]
    # if from_wishlist:
    #    update.callback_query.data += "_%s" % page
    #    view_wishlist(update, context)
    # else:
    logger.info("THIS IS THE CALL [%s]" % update.callback_query.data)
    view_wishlist_element_links(update, context)
    logger.info("CLOSING...")
    return ConversationHandler.END


ADD_NEW_LINK_TO_ELEMENT_CONVERSATION = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            callback=ask_for_new_link, pattern="ask_for_wishlist_element_link"
        ),
        CallbackQueryHandler(callback=ask_for_new_link, pattern="afwel_link"),
    ],
    states={
        APPEND_LINK: [
            MessageHandler(Filters.entity("url"), append_link),
            CallbackQueryHandler(
                callback=show_step_two_toast, pattern="show_step_2_advance"
            ),
            CallbackQueryHandler(
                callback=complete_operation, pattern="finish_new_link_insert"
            ),
        ]
    },
    fallbacks=[
        CallbackQueryHandler(
            callback=cancel_link_append, pattern="cancel_new_wishlist_element_link"
        ),
    ],
)
