#!/usr/bin/env python3

""" File that contains the class to start the bot with the bot api """

from datetime import date, datetime, time
from operator import index
import subprocess
import os
from random import random
import random
import re

from telegram.chat import Chat
from telegram.error import BadRequest
from root.contants.keyboard import create_switch_bot_keyboard
from root.handlers.new_group_handler import handle_new_group
from root.manager.notification_hander import show_notifications
from root.manager.admin_handler import handle_admin
from root.manager.deal_test_handler import command_send_deal
from root.job.update_product import (
    close_deal_notification,
    read_deal_notification,
    update_products,
)
from root.manager.wishlist_element_link import (
    ADD_NEW_LINK_TO_ELEMENT_CONVERSATION,
    delete_wishlist_element_link,
    show_price_popup,
    update_list,
    view_wishlist_element_links,
)

from telegram.ext.conversationhandler import ConversationHandler
from root.manager.change_element_wishlist import CHANGE_WISHLIST_ELEMENT_LIST
from root.manager.rename_wishlist import EDIT_WISHLIST_NAME
from root.manager.view_other_wishlists import (
    view_other_wishlists,
    reorder_wishlist,
)
from root.manager.wishlist_elements_middleware import (
    ask_delete_wishlist_list,
    change_current_wishlist,
    confirm_delete_wishlist_list,
    view_wishlist_conv_end,
)
from root.manager.advertisement_handler import (
    command_send_advertisement,
    send_advertisement,
)
from telegram_utils.utils.misc import environment

from telegram_utils.utils.tutils import delete_if_private, delete_message
from root.manager.wishlist_element_photo import (
    ADD_WISHLIST_PHOTO_CONVERSATION,
    abort_delete_all_wishlist_element_photos,
    ask_delete_all_wishlist_element_photos,
    confirm_delete_all_wishlist_element_photos,
    delete_photos_and_go_to_wishlist_element,
    delete_wishlist_element_photo,
    extract_photo_from_message,
    view_wishlist_element_photos,
)
from root.manager.edit_wishlist_element import EDIT_WISHLIST_CONVERSATION
from root.contants.messages import (
    MONTHLY_REPORT_POPUP_MESSAGE,
    SUPPORTED_LINKS_MESSAGE,
    YEARLY_REPORT_POPUP_MESSAGE,
)
from root.manager.convert_to_purchase import (
    ask_confirm_deletion,
    wishlist_element_confirm_convertion,
)
from root.manager.retrieve_purchase import update_purchases_for_chat
from root.manager.user_settings import settings_toggle_purchase_tips, view_user_settings
from root.manager.wishlist_element import (
    ADD_IN_WISHLIST_CONVERSATION,
    abort_delete_all_wishlist_elements,
    abort_delete_item_wishlist_element,
    ask_delete_all_wishlist_elements,
    confirm_delete_all_wishlist_elements,
    confirm_wishlist_element_deletion,
    remove_wishlist_element_item,
    toggle_element_action_page,
    view_wishlist,
)
from root.manager.bulk_delete import bulk_delete, cancel_bulk_delete
from telegram.ext.messagehandler import MessageHandler

from telegram.ext.pollanswerhandler import PollAnswerHandler
from root.manager.rating import Rating
from root.manager.purchase.handle_purchase import (
    confirm_purchase,
    discard_purchase,
    toggle_purchase_tips,
)
from telegram import Message, Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    CallbackQueryHandler,
    Dispatcher,
    Updater,
    Filters,
)

from root.model.purchase import Purchase
from root.manager.error import handle_error
from root.util.util import retrieve_key, is_group_allowed, is_develop
from root.manager.purchase.month_report import MonthReport
from root.manager.purchase.year_report import YearReport
from root.manager.purchase.compare import year_compare, month_compare
from root.manager.purchase.month_purchase import month_purchase
from root.manager.purchase.year_purchase import year_purchase
from root.manager.purchase.last import last_purchase
from root.manager.purchase.delete import delete_purchase
import root.util.logger as logger
from root.manager.help import bot_help, help_navigate, help_init
from root.helper.user_helper import is_admin, create_user, user_exists
from root.util.telegram import TelegramSender
from root.manager.start import (
    handle_start,
    help_end,
    append_commands,
    navigate_command_list,
    remove_commands,
    show_info,
)
from root.manager.feedback import FEEDBACK_CONVERSATION
from telegram_utils.utils.tutils import log
import root.manager.view_other_wishlists as view_other_wishlists
import subprocess


ADD_NEW_WISHLIST = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            view_other_wishlists.add_wishlist, pattern="add_new_wishlist"
        ),
    ],
    states={
        view_other_wishlists.INSERT_TITLE: [
            MessageHandler(Filters.text, view_other_wishlists.handle_add_confirm),
            CallbackQueryHandler(
                view_other_wishlists.handle_keep_confirm, pattern="keep_the_current"
            ),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(
            view_other_wishlists.cancel_add_wishlist, pattern="cancel_add_to_wishlist"
        ),
        CallbackQueryHandler(
            view_wishlist_conv_end,
            pattern="cancel_from_element_add_to_wishlist",
        ),
    ],
)


class BotManager:
    """The class to manage the bot"""

    def __init__(self):
        self.updater: Updater = None
        self.disp: Dispatcher = None
        self.token: str = None
        self.sender = TelegramSender()
        self.month_report = MonthReport()
        self.year_report = YearReport()

    def connect(self):
        """Run the telegram bot"""
        self.token = retrieve_key("TOKEN")
        self.updater = Updater(
            self.token,
            use_context=True,
            request_kwargs={},
        )
        self.disp = self.updater.dispatcher
        self.add_handler()
        logger.info("Il bot si sta avviando...")
        logger.info("Start polling...")
        self.updater.start_polling(clean=True)

    def restart(self, update: Update, context: CallbackContext):
        """Restart the bot by using systemctl

        Args:
            update (Update): Telegram update
            context (CallbackContext): The context of the telegram bot
        """
        message: Message = update.message if update.message else update.edited_message
        chat_id = message.chat.id
        user_id = update.effective_user.id
        if not user_exists(user_id):
            create_user(update.effective_user)
            return
        if is_admin(user_id):
            self.sender.send_and_delete(
                update.effective_message.message_id,
                update.effective_user.id,
                context,
                chat_id,
                "Riavvio il bot...",
                timeout=10,
            )
            if is_develop():
                os.popen("sudo systemctl restart last-purchase-quality")
            else:
                os.popen("sudo systemctl restart last-purchase")

    def send_git_link(self, update: Update, context: CallbackContext):
        """Send the link to the github page of this project

        Args:
            update (Update): Telegram update
            context (CallbackContext): The context of the telegram bot
        """
        message: Message = update.message if update.message else update.edited_message
        chat_id = message.chat.id
        if not is_group_allowed(chat_id):
            return
        chat_id = update.effective_message.chat.id
        self.sender.send_and_delete(
            update.effective_message.message_id,
            update.effective_user.id,
            context,
            chat_id=chat_id,
            text="https://github.com/VGsNETWORK/ultimi-acquisti",
        )

    def show_alert(self, update: Update, context: CallbackContext, message: str):
        context.bot.answer_callback_query(
            update.callback_query.id, text=message, show_alert=True
        )

    def empty_button(self, update: Update, context: CallbackContext):
        """The Callback called when the button does nothing

        Args:
            update (Update): Telegram update
            context (CallbackContext): The context of the telegram bot
        """
        context.bot.answer_callback_query(update.callback_query.id)

    def delete_all_purchases(self, update: Update, context: CallbackContext):
        if is_develop():
            Purchase.objects.delete()
            context.bot.send_message(
                chat_id=update.effective_chat.id, text="✅  Acquisti cancellati"
            )
        else:
            logger.info("this is not a development environment, ARE YOU CRAZY?")

    def switch_bot(self, update: Update, context: CallbackContext):
        logger.info("switching bot...")
        message: Message = update.effective_message
        chat: Chat = update.effective_chat
        if not update.callback_query:
            text: str = message.text
            bot: str = re.sub("\/\w+(\s)?", "", text)
        else:
            bot: str = update.callback_query.data
            bot: str = bot.split("_")[-1]
        # self.sender.delete_previous_message(
        #    update.effective_user.id, message.message_id, chat.id, context
        # )
        try:
            self.sender.delete_if_private(context, update.effective_message)
            logger.info("THIS IS THE NEW BOT [%s]" % bot)
            if message.chat.type == "private":
                if not bot:
                    keyboard = create_switch_bot_keyboard()
                    context.bot.send_message(
                        chat_id=chat.id,
                        text=(
                            "Seleziona il servizio da avviare:\n\n"
                            "In alternativa, puoi usare il comando  <code>/switch vgs-antispam-quality</code>."
                        ),
                        reply_markup=keyboard,
                        disable_web_page_preview=True,
                        parse_mode="HTML",
                    )
                    return
                status = os.path.isfile("/etc/systemd/system/%s.service" % bot)
                if update.callback_query:
                    status = True
                if not status:
                    context.bot.send_message(
                        chat_id=chat.id,
                        text=(
                            "L'argomento  <code>&lt;nome-servizio&gt;</code>  del comando  <code>/switch</code>  "
                            "può avere i seguenti valori:\n"
                            "    -  <code>vgs-antispam-quality</code>\n"
                            "    -  <code>last-purchase-quality</code>\n\n"
                            "In alternativa, puoi usare il comando  <code>/switch</code>  senza argomenti."
                        ),
                        disable_web_page_preview=True,
                        parse_mode="HTML",
                    )
                    return
                if bot == "last-purchase-quality":
                    context.bot.send_message(
                        chat_id=chat.id,
                        text="Il servizio  <code>last-purchase-quality</code>  è già online.",
                        disable_web_page_preview=True,
                        parse_mode="HTML",
                    )
                    return
                # context.bot.send_message(
                #    chat_id=chat.id,
                #    text="Cambio il bot con <code>%s</code>." % bot,
                #    disable_web_page_preview=True,
                #    parse_mode="HTML",
                # )
                logger.info(
                    "/opt/bot/network/quality/scripts/switch_from_purchase.sh %s" % bot
                )
                subprocess.check_call(
                    ["/opt/bot/network/quality/scripts/switch_from_purchase.sh", bot]
                )
        except BadRequest:
            context.bot.send_message(
                chat_id=chat.id,
                text="❌  Non sono riuscito a fare lo switch con il bot <code>%s</code>."
                % bot,
                disable_web_page_preview=True,
                parse_mode="HTML",
            )

    def delete_message(self, update: Update, context: CallbackContext):
        context.bot.answer_callback_query(update.callback_query.id)
        context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id,
        )

    def add_handler(self):
        """Add handlers for the various operations"""
        rating = Rating()

        if environment("PROFILE") != "develop":
            # update all products every 30 minutes
            self.disp.job_queue.run_repeating(
                interval=900, first=0, callback=update_products
            )

        self.disp.job_queue.stop()
        try:
            hours = [10, 12, 15, 17]
            whens = [time(hour=h, minute=0) for h in hours]
            groups = retrieve_key("AD_GROUPS")
            if not groups:
                logger.error("EMPTY AD GROUPS")
                groups = []
            else:
                groups = eval(groups)
            days = [1, 4, 8, 12, 17, 23, 26, 30]
            logger.info("TOTAL NUMBER OF GROUPS FOR ADS %s" % len(groups))
            message = []
            for index in range(0, len(groups)):
                # fmt: off
                group = groups[0]; groups.remove(group)
                when = whens[0]; whens.remove(when)
                chat = self.disp.bot.get_chat(chat_id=group)
                group_name = chat.title.split(" | ")[0]
                message.append(f"\n<b>{group_name}</b>")
                # fmt: on
                for i in range(0, 2):
                    day = days[0]
                    days.remove(day)
                    message.append(
                        f"    👷🏻‍♂️ Aggiunto scheduler di advertising per il giorno <b>{day}</b> di ogni mese alle ore <b>{when.hour + 2}:00</b>",
                    )
                    logger.info(message)
                    self.disp.job_queue.run_monthly(
                        callback=send_advertisement,
                        context={"group": group},
                        day=day,
                        when=when,
                    )
            message = "\n".join(message)
            log(0, message)
        except Exception as e:
            logger.error(e)
        logger.info("adding test commands")

        if is_develop():
            logger.info("adding test commands")
            self.disp.add_handler(CommandHandler("ad", command_send_advertisement))
            self.disp.add_handler(CommandHandler("err", handle_error))
            self.disp.add_handler(CommandHandler("deal", command_send_deal))
            self.disp.add_handler(CommandHandler("switch", self.switch_bot))
            self.disp.add_handler(
                CallbackQueryHandler(pattern="switch_bot", callback=self.switch_bot)
            )

        self.disp.add_handler(
            CallbackQueryHandler(
                pattern="close_deal_notification", callback=close_deal_notification
            )
        )
        self.disp.add_handler(
            CallbackQueryHandler(
                pattern="read_deal_notification", callback=read_deal_notification
            )
        )

        self.disp.add_handler(
            MessageHandler(Filters.status_update.new_chat_members, handle_new_group)
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                pattern="show_notifications", callback=show_notifications
            )
        )

        self.disp.add_handler(CommandHandler("aggiorna", update_purchases_for_chat))

        self.disp.add_handler(CommandHandler("impostazioni", view_user_settings))

        self.disp.add_handler(
            CallbackQueryHandler(pattern="spp", callback=show_price_popup)
        )
        self.disp.add_handler(
            CallbackQueryHandler(pattern="show_admin_panel", callback=handle_admin)
        )

        self.disp.add_handler(CommandHandler("vota", rating.poll))
        self.disp.add_handler(
            CallbackQueryHandler(pattern="rating_menu", callback=rating.poll)
        )
        self.disp.add_handler(
            CallbackQueryHandler(pattern="rwel", callback=delete_wishlist_element_link)
        )
        self.disp.add_handler(ADD_NEW_LINK_TO_ELEMENT_CONVERSATION)
        self.disp.add_handler(
            CallbackQueryHandler(
                pattern="view_wishlist_link_element",
                callback=view_wishlist_element_links,
            )
        )
        self.disp.add_handler(
            CallbackQueryHandler(
                pattern="update_wishlist_link_element", callback=update_list
            )
        )
        self.disp.add_handler(
            CallbackQueryHandler(
                pattern="previous_rating", callback=rating.go_back_rating
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                pattern="view_other_wishlists",
                callback=view_other_wishlists.view_other_wishlists,
            )
        )

        # self.disp.add_handler(MessageHandler(Filters.photo, extract_photo_from_message))
        self.disp.add_handler(ADD_WISHLIST_PHOTO_CONVERSATION)
        self.disp.add_handler(ADD_IN_WISHLIST_CONVERSATION)
        self.disp.add_handler(
            MessageHandler(
                Filters.photo,
                lambda update, context: delete_if_private(update.effective_message),
            )
        )
        self.disp.add_handler(
            CallbackQueryHandler(reorder_wishlist, pattern="reorder_wishlist")
        )
        self.disp.add_handler(
            CallbackQueryHandler(
                change_current_wishlist, pattern="change_current_wishlist"
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                ask_delete_wishlist_list,
                pattern="ask_delete_wishlist_and_elements",
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                toggle_element_action_page, pattern="toggle_element_action_page"
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                confirm_delete_wishlist_list, pattern="confirm_delete_wishlist_list"
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(self.delete_message, pattern="delete_message")
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                abort_delete_item_wishlist_element,
                pattern="cancel_remove_wishlist_element",
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                pattern="ask_delete_all_wishlist_element_photos",
                callback=ask_delete_all_wishlist_element_photos,
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                pattern="confirm_delete_all_wishlist_element_photos",
                callback=confirm_delete_all_wishlist_element_photos,
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                pattern="abort_delete_all_wishlist_element_photos",
                callback=abort_delete_all_wishlist_element_photos,
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                pattern="ask_delete_all_wishlist_elements",
                callback=ask_delete_all_wishlist_elements,
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                pattern="confirm_delete_all_wishlist_element",
                callback=confirm_delete_all_wishlist_elements,
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                pattern="abort_delete_all_wishlist_element",
                callback=abort_delete_all_wishlist_elements,
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                pattern="go_back_from_wishlist_element_photos",
                callback=delete_photos_and_go_to_wishlist_element,
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                pattern="delete_wishlist_element_photo",
                callback=delete_wishlist_element_photo,
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                pattern="view_wishlist_element_photo",
                callback=view_wishlist_element_photos,
            )
        )

        self.disp.add_handler(PollAnswerHandler(rating.receive_poll_answer))
        self.disp.add_error_handler(handle_error)
        self.disp.add_handler(CHANGE_WISHLIST_ELEMENT_LIST)
        self.disp.add_handler(FEEDBACK_CONVERSATION)
        self.disp.add_handler(EDIT_WISHLIST_NAME)
        self.disp.add_handler(ADD_NEW_WISHLIST)
        self.disp.add_handler(
            CallbackQueryHandler(
                pattern="show_supported_link",
                callback=lambda update, context: context.bot.answer_callback_query(
                    update.callback_query.id,
                    text=SUPPORTED_LINKS_MESSAGE,
                    show_alert=True,
                ),
            )
        )
        self.disp.add_handler(
            CommandHandler(
                "start",
                view_user_settings,
                Filters.regex("show_settings"),
            )
        )

        self.disp.add_handler(
            CommandHandler(
                "start",
                rating.poll,
                Filters.regex("vote"),
            )
        )

        self.disp.add_handler(
            CommandHandler(
                "start",
                show_info,
                Filters.regex("show_info"),
            )
        )

        self.disp.add_handler(
            CommandHandler(
                "start",
                bot_help,
                Filters.regex("how_to"),
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                pattern="convert_to_purchase",
                callback=ask_confirm_deletion,
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                pattern="delete_wish_and_create_purchase_link",
                callback=wishlist_element_confirm_convertion,
            )
        )

        self.disp.add_handler(EDIT_WISHLIST_CONVERSATION)

        self.disp.add_handler(
            CallbackQueryHandler(
                pattern="monthly_report_info",
                callback=lambda update, context: self.show_alert(
                    update, context, MONTHLY_REPORT_POPUP_MESSAGE
                ),
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                pattern="yearly_report_info",
                callback=lambda update, context: self.show_alert(
                    update, context, YEARLY_REPORT_POPUP_MESSAGE
                ),
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                confirm_wishlist_element_deletion,
                pattern="confirm_remove_wishlist_element",
            )
        )

        self.disp.add_handler(CommandHandler("l33t", bulk_delete))
        self.disp.add_handler(CommandHandler("cancellastorico", bulk_delete))
        self.disp.add_handler(
            CallbackQueryHandler(callback=bulk_delete, pattern="confirm_bulk_delete")
        )
        self.disp.add_handler(
            CallbackQueryHandler(
                callback=cancel_bulk_delete, pattern="cancel_bulk_delete"
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                callback=view_wishlist, pattern="view_wishlist_element"
            )
        )

        self.disp.add_handler(CommandHandler("wishlist", view_wishlist))

        self.disp.add_handler(
            CallbackQueryHandler(
                callback=remove_wishlist_element_item, pattern="remove_wishlist_element"
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(callback=view_user_settings, pattern="user_settings")
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                callback=settings_toggle_purchase_tips, pattern="settings_toggle_tips"
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(callback=rating.cancel_rating, pattern="cancel_rating")
        )
        self.disp.add_handler(
            CallbackQueryHandler(callback=rating.send_feedback, pattern="skip_rating")
        )
        self.disp.add_handler(
            CommandHandler(
                "start",
                self.month_report.month_report,
                Filters.regex("monthly_report"),
            )
        )
        self.disp.add_handler(
            CommandHandler(
                "start",
                self.year_report.year_report,
                Filters.regex("yearly_report"),
            )
        )
        self.disp.add_handler(
            CommandHandler(
                "start",
                last_purchase,
                Filters.regex("last_purchase"),
            )
        )
        self.disp.add_handler(
            CommandHandler(
                "start",
                month_purchase,
                Filters.regex("monthly_expense"),
            )
        )
        self.disp.add_handler(
            CommandHandler(
                "start",
                year_purchase,
                Filters.regex("yearly_expense"),
            )
        )
        self.disp.add_handler(
            CommandHandler(
                "start",
                view_wishlist,
                Filters.regex("wishlist"),
            )
        )
        self.disp.add_handler(CommandHandler("start", handle_start))
        self.disp.add_handler(CommandHandler("git", self.send_git_link))
        self.disp.add_handler(CommandHandler("restart", self.restart))
        self.disp.add_handler(CommandHandler("howto", help_init))
        self.disp.add_handler(
            CallbackQueryHandler(callback=help_navigate, pattern="how_to_page_.*")
        )
        self.disp.add_handler(
            CallbackQueryHandler(callback=help_end, pattern="how_to_end")
        )
        self.disp.add_handler(CommandHandler("cancellaspesa", delete_purchase))
        self.disp.add_handler(CommandHandler("ultimoacquisto", last_purchase))
        self.disp.add_handler(CommandHandler("comparamese", month_compare))
        self.disp.add_handler(CommandHandler("comparaanno", year_compare))
        self.disp.add_handler(CommandHandler("spesaannuale", year_purchase))
        self.disp.add_handler(CommandHandler("spesamensile", month_purchase))

        self.disp.add_handler(
            CommandHandler("reportannuale", self.year_report.year_report)
        )

        self.disp.add_handler(CommandHandler("info", show_info))

        self.disp.add_handler(
            CallbackQueryHandler(callback=show_info, pattern="show_bot_info")
        )

        self.disp.add_handler(
            CallbackQueryHandler(callback=show_info, pattern="expand_info")
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                callback=rating.approve_rating, pattern="approve_feedback"
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(callback=rating.start_poll, pattern="start_poll")
        )

        self.disp.add_handler(
            CallbackQueryHandler(callback=rating.show_rating, pattern="show_rating")
        )

        self.disp.add_handler(
            CallbackQueryHandler(callback=rating.deny_rating, pattern="deny_feedback")
        )
        self.disp.add_handler(
            CallbackQueryHandler(
                callback=rating.delete_reviewed_rating_message,
                pattern="delete_reviewed_rating_message",
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                callback=navigate_command_list, pattern="command_page_.*"
            )
        )
        self.disp.add_handler(
            CallbackQueryHandler(
                callback=self.year_report.previous_year, pattern="year_previous_year"
            )
        )
        self.disp.add_handler(
            CallbackQueryHandler(
                callback=self.year_report.next_year, pattern="year_next_year"
            )
        )

        self.disp.add_handler(
            CommandHandler("reportmensile", self.month_report.month_report)
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                callback=self.month_report.previous_page, pattern="month_previous_page"
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                callback=self.month_report.next_page, pattern="month_next_page"
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                callback=self.month_report.next_year, pattern="month_next_year"
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                callback=self.month_report.previous_year, pattern="month_previous_year"
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                callback=self.month_report.current_month_report,
                pattern="month_first_month",
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(callback=self.empty_button, pattern="empty_button")
        )
        self.disp.add_handler(
            CallbackQueryHandler(
                callback=self.month_report.expand_report, pattern="expand_report.*"
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                callback=self.year_report.expand_report, pattern="expand_year_report.*"
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                callback=append_commands, pattern="start_show_commands"
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                callback=remove_commands, pattern="start_hide_commands"
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                callback=toggle_purchase_tips, pattern="purchase.toggle_tips"
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                callback=toggle_purchase_tips, pattern="purchase.toggle_tips"
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                callback=confirm_purchase, pattern="confirm_purchase_*"
            )
        )

        self.disp.add_handler(
            CallbackQueryHandler(callback=discard_purchase, pattern="remove_purchase_*")
        )

        if is_develop():
            self.disp.add_handler(CommandHandler("h4x0r", self.delete_all_purchases))

        self.disp.add_handler(
            MessageHandler(callback=rating.send_feedback, filters=Filters.text)
        )
