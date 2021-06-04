#!/usr/bin/env python3

""" File that contains the class to start the bot with the bot api """

import os
from re import A
from root.manager.edit_wishlist import EDIT_WISHLIST_CONVERSATION
from root.contants.messages import (
    MONTHLY_REPORT_POPUP_MESSAGE,
    YEARLY_REPORT_POPUP_MESSAGE,
)
from root.manager.convert_to_purchase import (
    ask_confirm_deletion,
    wishlist_confirm_convertion,
)
from root.manager.retrieve_purchase import update_purchases_for_chat
from root.manager.user_settings import settings_toggle_purchase_tips, view_user_settings
from root.manager.whishlist import (
    ADD_IN_WISHLIST_CONVERSATION,
    confirm_wishlist_deletion,
    remove_wishlist_item,
    view_wishlist,
)
from root.manager.bulk_delete import bulk_delete, cancel_bulk_delete
import telegram
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
            os.popen("sudo systemctl restart last-purchase")

    def send_git_link(self, update: Update, context: CallbackContext):
        """Send the link to the gitlab page of this project

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
            text="https://gitlab.com/nautilor/ultimi-acquisti",
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

    def add_handler(self):
        """Add handlers for the various operations"""
        rating = Rating()
        self.disp.add_handler(CommandHandler("aggiorna", update_purchases_for_chat))
        self.disp.add_handler(
            CallbackQueryHandler(pattern="rating_menu", callback=rating.poll)
        )
        self.disp.add_handler(
            CallbackQueryHandler(
                pattern="previous_rating", callback=rating.go_back_rating
            )
        )

        self.disp.add_handler(PollAnswerHandler(rating.receive_poll_answer))
        self.disp.add_error_handler(handle_error)
        self.disp.add_handler(FEEDBACK_CONVERSATION)
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
                callback=wishlist_confirm_convertion,
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
                confirm_wishlist_deletion, pattern="confirm_remove_wishlist"
            )
        )

        self.disp.add_handler(ADD_IN_WISHLIST_CONVERSATION)
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
            CallbackQueryHandler(callback=view_wishlist, pattern="view_wishlist")
        )

        self.disp.add_handler(
            CallbackQueryHandler(
                callback=remove_wishlist_item, pattern="remove_wishlist"
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
