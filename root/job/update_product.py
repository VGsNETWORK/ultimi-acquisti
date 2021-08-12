#!/usr/bin/env python3

# IMPORTS
# region
from re import sub
from root.helper.wishlist_element import find_containing_link
from root.util.util import format_price
from telegram_utils.utils.misc import format_error
from root.helper.user_helper import retrieve_user
from root.model.subscriber import Subscriber
from root.helper.subscriber_helper import find_subscriber, update_subscriber
from root.contants.messages import DEAL_MESSAGE_FORMAT, DEAL_MESSAGE_FORMAT_APPEND
from root.model.tracked_link import TrackedLink
from typing import List
from root.helper.tracked_link_helper import (
    find_link_by_code,
    get_paged_link,
    get_total_pages,
    update_or_create_scraped_link,
)
from telegram.ext import CallbackContext
import telegram_utils.utils.logger as logger
from telegram.error import BadRequest
from root.handlers.handlers import extractor
import math

# endregion


def send_deal(product: TrackedLink, previous_price: float, context: CallbackContext):
    """send a deal to all it's subscribers"""
    subscribers: List[int] = product.subscribers
    for subscriber in subscribers:
        try:
            user_id: int = subscriber
            # retrieve the difference from the previous price
            subscriber: Subscriber = find_subscriber(subscriber, product.code)
            if not subscriber:
                logger.info("creating subscriber")
                update_subscriber(user_id, product.code, previous_price)
                subscriber: Subscriber = find_subscriber(subscriber, product.code)
            logger.info("found subscriber %s" % user_id)
            if product.price < subscriber.lowest_price:
                logger.info("creating price diff to %s" % user_id)
                price_diff = subscriber.lowest_price - product.price
                logger.info("updating deal for %s" % user_id)
                update_subscriber(subscriber.user_id, product.code, product.price)
                # split the title if it's too long
                url = "%s/%s" % (product.base_url, product.code)
                perc = (math.ceil((price_diff) * subscriber.lowest_price / 100),)
                message = DEAL_MESSAGE_FORMAT % (
                    url,
                    find_containing_link(url),
                    perc,
                    format_price(price_diff),
                    format_price(product.price),
                    DEAL_MESSAGE_FORMAT_APPEND if perc > 30 else "",
                )
                logger.info("sending deal to %s" % user_id)
                user = retrieve_user(subscriber.user_id)
                chat_id = user.channel if user.channel else subscriber.user_id
                try:
                    context.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        disable_web_page_preview=True,
                        parse_mode="HTML",
                    )
                except BadRequest as br:
                    logger.error(format_error(br))
            else:
                logger.info(
                    "ignoring user %s since his price is lower than %s"
                    % (subscriber.user_id, product.price)
                )
        except BadRequest:
            continue


def update_products(context: CallbackContext):
    """update all products in the database"""
    logger.info("Updating database products")
    total_pages = get_total_pages()
    for page in range(total_pages):
        logger.info("querying page %s" % page)
        products: List[TrackedLink] = get_paged_link(page=page)
        for product in products:
            logger.info("querying product %s" % product.code)
            if not product.code.startswith("//"):
                previous_price: float = product.price
                logger.info("loading %s/%s" % (product.base_url, product.code))
                product: dict = extractor.parse_url(
                    "%s/%s" % (product.base_url, product.code)
                )
                if product["code"].startswith("/"):
                    product["code"] = product["code"][1:]
                updated: bool = update_or_create_scraped_link(product)
                if updated:
                    product: TrackedLink = find_link_by_code(product["code"])
                    if int(product.price) == 0:
                        logger.warn("product %s price is 0, resetting" % product.code)
                        product.price = previous_price
                        product.save()
                        continue
                    if product.price > previous_price:
                        logger.warn(
                            "product %s price is raised, resetting" % product.code
                        )
                        # ! Please look into this
                        # product.price = previous_price
                        product.save()
                    if product.price < previous_price:
                        logger.info("that's what i call a deal for %s" % product.code)
                        send_deal(product, previous_price, context)
            else:
                product.delete()
