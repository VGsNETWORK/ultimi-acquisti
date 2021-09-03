#!/usr/bin/env python3


from datetime import datetime
from root.manager.command_redirect import command_redirect

from mongoengine.errors import DoesNotExist
from root.model.configuration import Configuration
from typing import ContextManager, List
from telegram import poll, user
import numpy as np


from telegram.callbackquery import CallbackQuery
from root.helper.user_helper import create_user, retrieve_user
from telegram.message import Message
from telegram.user import User
from root.model.user_rating import UserRating
from root.util.util import create_button, retrieve_key
from root.manager.start import rating_cancelled, remove_commands
from root.helper.configuration import ConfigurationHelper
from root.contants.keyboard import (
    RATING_KEYBOARD,
    RATING_REVIEWED_KEYBOARD,
    SHOW_RATING_KEYBOARD,
    build_approve_keyboard,
    build_pre_poll_keyboard,
)
from telegram.ext.callbackcontext import CallbackContext
from telegram.error import BadRequest
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.update import Update
from root.contants.messages import (
    RATING_PLACEHOLDER,
    RATING_VALUES,
    USER_ALREADY_VOTED,
    USER_ALREADY_VOTED_APPROVED,
    USER_ALREADY_VOTED_BOTH,
    USER_ALREADY_VOTED_TO_APPROVE,
    USER_HAS_NO_VOTE,
    USER_MESSAGE_REVIEW_APPROVED_FROM_STAFF,
    USER_MESSAGE_REVIEW_NOT_APPROVED_FROM_STAFF,
    build_approve_rating_message,
    build_show_rating_message,
)
from uuid import uuid4
import root.util.logger as logger
import re
from root.util.telegram import TelegramSender

sender = TelegramSender()

class Rating:
    def __init__(self):
        self.status_index = {}
        self.status = {}
        self.feedback = {}
        self.message_id = {}
        self.user_message = {}
        self.previous_votes = {}
        self.previous_comments = {}
        self.configuration_helper = ConfigurationHelper()
        self.MAX_CHARACTERS_ALLOWED = 256
        self.MAX_CHARACTERS_SPLIT = 400

    def save_to_database(self, user_id: int, context: CallbackContext, user: User):
        data = self.feedback[user_id]
        args = []
        for vote in data:
            for key in vote.keys():
                if isinstance(vote[key], str):
                    args.append(re.sub(r"^\<.*\>$|\"", "", vote[key]))
                else:
                    args.append(vote[key])
        code = str(uuid4()).replace("-", "")[5:20]
        feedback_channel = retrieve_key("FEEDBACK_CHANNEL")
        user_rating: UserRating = UserRating(
            approve_message_id=0,
            approve_chat_id=feedback_channel,
            code=code,
            user_id=user_id,
            ux_vote=args[0],
            ux_comment=args[1],
            functionality_vote=args[2],
            functionality_comment=args[3],
            ui_vote=args[4],
            ui_comment=args[5],
            overall_vote=args[6],
            overall_comment=args[7],
        )
        if not retrieve_user(user.id):
            create_user(user)
        message: Message = context.bot.send_message(
            text=build_approve_rating_message(user_rating, user),
            chat_id=feedback_channel,
            reply_markup=build_approve_keyboard(code, user_id),
            disable_web_page_preview=True,
            parse_mode="HTML",
        )
        user_rating.approve_message_id = message.message_id
        user_ratings = UserRating.objects.filter(
            user_id=user_id, approved=False
        ).order_by("creation_date")
        if len(user_ratings) == 1:
            rating: UserRating = user_ratings[0]
            context.bot.delete_message(
                chat_id=rating.approve_chat_id, message_id=rating.approve_message_id
            )
            rating.delete()

        user_rating.save()

    def send_feedback(self, update: Update, context: CallbackContext):
        if update.effective_chat.type == "channel":
            return
        if not update.effective_user.id == update.effective_chat.id:
            return
        user_id = update.effective_user.id
        if not user_id in self.status_index:
            return
        if self.status_index[user_id] == 0:
            return
        logger.info("ricevuto feedback")
        chat_id = update.effective_chat.id
        message_id = update.effective_message.message_id
        text = update.effective_message.text
        if len(text) > self.MAX_CHARACTERS_ALLOWED and not update.callback_query:
            boundary = len(text) - self.MAX_CHARACTERS_ALLOWED
            user_text = text[: self.MAX_CHARACTERS_SPLIT]
            user_text = [t for t in user_text]
            user_text.insert(self.MAX_CHARACTERS_ALLOWED, "<s>")
            user_text.append("</s>")
            user_text = "".join(user_text)
            context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            text = self.user_message[user_id]
            text += f"\n\n\n🚫  <b>Limite superato di {boundary} caratteri!</b>"
            text += f'\nEcco quello che hai inserito (tagliato a {self.MAX_CHARACTERS_ALLOWED} caratteri):\n<i>"{user_text}"</i>'
            text += f"\n\n<b>Inserisci un commento (massimo {self.MAX_CHARACTERS_ALLOWED} caratteri):</b>"
            text += "\n💡 <i>Ricorda che un voto senza commento ha meno incidenza sulla <b>media pubblica</b>.</i>"
            try:
                context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=self.message_id[user_id],
                    text=text,
                    reply_markup=InlineKeyboardMarkup(RATING_KEYBOARD),
                    parse_mode="HTML",
                )
            except BadRequest:
                pass
            return
        if not update.callback_query:
            text = f'"{text}"'
        else:
            text = "<b>Non presente</b>"
        index = self.status_index[user_id] if self.status_index[user_id] >= 0 else 0
        vote = self.feedback[user_id][index - 1]["vote"]
        message_vote = vote * "⭐️"
        message_vote += "🕳" * (5 - vote)
        vote = message_vote
        if self.status_index[user_id] == 1:
            self.user_message[
                user_id
            ] = f"<b>{RATING_VALUES[index - 1]}</b>\n– Voto:  {vote}\n– Commento:  <i>{text}</i>"
        else:
            self.user_message[user_id] += f"\n– Commento:  <i>{text}</i>"
        context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=self.message_id[user_id],
            text=self.user_message[user_id] + "\n\n\n<b>Dai un voto a...</b>",
            parse_mode="HTML",
        )
        if text != "<b>Non presente</b>":
            context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        self.feedback[user_id][index - 1]["message"] = text
        if not index >= len(RATING_VALUES):
            logger.info(f"deleting {message_id - 1}")
            status = RATING_VALUES[index]
            logger.info(f"creo con index {index}")
            self.create_poll(f"{status}", chat_id, context)
            return

        logger.info("setting status to -1")
        self.status_index[user_id] = 0
        self.status[user_id] = RATING_VALUES[0]
        context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=self.message_id[user_id],
            text=f"{self.user_message[user_id]}\n\n\n<b>Grazie per aver votato!</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        create_button(
                            "↩️  Torna indietro",
                            "rating_menu",
                            "rating_menu",
                        )
                    ]
                ]
            ),
        )
        logger.info(self.feedback)
        logger.info("Conversation with user finished")
        self.save_to_database(user_id, context, update.effective_user)

    def create_poll(
        self,
        text: str,
        chat_id: int,
        context: CallbackContext,
        answers=["⭐️" * i for i in range(1, 6)],
    ):
        answers = list(answers)
        answers.append("❌  Annulla")
        index = self.status_index[chat_id] if self.status_index[chat_id] >= 0 else 0
        message = ""
        previous = ""
        if chat_id in self.previous_votes:
            if self.previous_votes[chat_id]:
                vote = self.previous_votes[chat_id][index]
                stars = vote * "⭐️"
                stars += (5 - vote) * "🕳"
                message = f"\n\nVoto precedente:  {stars}"
                previous = f"  (prima:  {stars})"
        message = context.bot.send_poll(
            chat_id,
            f"{text}{previous}\n⠀",
            answers,
            is_anonymous=False,
            allows_multiple_answers=False,
        )
        payload = {
            message.poll.id: {
                "questions": answers,
                "message_id": message.message_id,
                "chat_id": chat_id,
                "answers": 0,
            }
        }
        context.bot_data.update(payload)

    def poll(self, update: Update, context: CallbackContext) -> None:
        if not update.effective_message.chat.type == "private":
            command_redirect("vota", "vote", update, context)
            return
        if update.callback_query:
            data = update.callback_query.data
        else:
            data = "rating_menu"
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        message_id = update.effective_message.message_id
        approved: UserRating = UserRating.objects.filter(user_id=user_id, approved=True)
        to_approve: UserRating = UserRating.objects.filter(
            user_id=user_id, approved=False
        )
        pr = None
        if approved or to_approve:
            message = USER_ALREADY_VOTED
            if approved:
                approved_message = f"<b>{len(approved)}</b> recensione pubblicata (✅)"
                approved = approved[0]
                pr = approved
            else:
                approved_message = ""
            if to_approve:
                to_approve_message = (
                    f"<b>{len(to_approve)}</b> recensione in fase di valutazione (⚖️)"
                )
                to_approve = to_approve[0]
                pr = to_approve
            else:
                to_approve_message = ""
            if approved and to_approve_message:
                message = message % (
                    approved_message,
                    " e ",
                    to_approve_message,
                    USER_ALREADY_VOTED_BOTH,
                )
            elif approved:
                message = message % (
                    approved_message,
                    "",
                    "",
                    USER_ALREADY_VOTED_APPROVED,
                )
            elif to_approve_message:
                message = message % (
                    to_approve_message,
                    "",
                    "",
                    USER_ALREADY_VOTED_TO_APPROVE,
                )
        else:
            message = USER_HAS_NO_VOTE

        if pr:
            # fmt: off
            self.previous_votes[user_id] = [pr.ux_vote, pr.functionality_vote, pr.ui_vote, pr.overall_vote]
            self.previous_comments[user_id] = [pr.ux_comment, pr.functionality_comment, pr.ui_comment, pr.overall_comment]
        else:
            self.previous_votes[user_id] = None
            self.previous_votes[user_id] = None
            # fmt: on
        if update.callback_query:
            context.bot.edit_message_text(
                chat_id=chat_id,
                text=message,
                message_id=message_id,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=build_pre_poll_keyboard(approved, to_approve, data),
            )
        else:
            sender.delete_if_private(context, update.effective_message)
            context.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=build_pre_poll_keyboard(approved, to_approve, data),
            )


    def show_rating(self, update: Update, context: CallbackContext):
        """ Show user rating """
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        message_id = update.effective_message.message_id
        callback: CallbackQuery = update.callback_query
        code = callback.data
        code = code.split("_")[-1]
        try:
            rating: UserRating = UserRating.objects.get(user_id=user_id, code=code)
            message = build_show_rating_message(rating)
            context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=message,
                reply_markup=SHOW_RATING_KEYBOARD,
                disable_web_page_preview=True,
                parse_mode="HTML",
            )
        except DoesNotExist:
            self.poll(update, context)

    def start_poll(self, update: Update, context: CallbackContext):
        """Sends a predefined poll"""
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        self.message_id[user_id] = context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=update.effective_message.message_id,
            text=RATING_PLACEHOLDER,
            disable_web_page_preview=True,
            parse_mode="HTML",
        ).message_id
        self.status_index[user_id] = 0
        self.status[user_id] = RATING_VALUES[0]
        self.feedback[user_id] = []
        self.user_message[user_id] = ""
        try:
            context.bot.delete_message(
                chat_id=chat_id, message_id=update.effective_message.message_id - 1
            )
        except BadRequest:
            pass
        self.create_poll(f"{self.status[user_id]}", chat_id, context)

    def receive_poll_answer(self, update: Update, context: CallbackContext) -> None:
        answer = update.poll_answer
        poll_id, first_name = answer.poll_id, answer.user.first_name
        user_id = answer.user.id
        poll_data = context.bot_data[poll_id]
        chat_id, message_id = poll_data["chat_id"], poll_data["message_id"]
        vote = answer.option_ids[0] + 1
        if vote == 6:
            self.status_index[user_id] = 0
            self.status[user_id] = RATING_VALUES[0]
            context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            rating_cancelled(update, context, self.message_id[user_id])
            return
        self.feedback[user_id].append({"vote": vote})
        logger.info(f"user {first_name} voted {vote}/5 ⭐️")

        context.bot.stop_poll(chat_id, message_id)
        index = self.status_index[user_id] if self.status_index[user_id] >= 0 else 0
        status = RATING_VALUES[index]
        stars = vote * "⭐️"
        stars += (5 - vote) * "🕳"

        if self.user_message[user_id]:
            text = f"\n\n<b>{status}</b>\n– Voto:  {stars}"
        else:
            text = f"<b>{status}</b>\n– Voto:  {stars}"
        self.user_message[user_id] += text
        previous_comment = ""
        if user_id in self.previous_comments:
            if self.previous_comments[user_id]:
                previous_comment = self.previous_comments[user_id][index]
                if previous_comment:
                    previous_comment = f'Commento precedente:  <i>"{previous_comment}"</i>\n\n'
                else:
                    previous_comment = ""
        try:
            context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=self.message_id[user_id],
                text=self.user_message[user_id]
                + f"\n\n\n{previous_comment}<b>Inserisci un commento (massimo {self.MAX_CHARACTERS_ALLOWED} caratteri):</b>\n"
                + "💡 <i>Ricorda che un voto senza commento ha meno incidenza sulla <b>media pubblica</b>.</i>",
                reply_markup=InlineKeyboardMarkup(RATING_KEYBOARD),
                parse_mode="HTML",
            )
        except BadRequest:
            pass
        self.status[user_id] = RATING_VALUES[self.status_index[user_id]]
        context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        self.status_index[user_id] += 1
        logger.info(self.status_index[user_id])

    def go_back_rating(self, update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        index = self.status_index[user_id] if self.status_index[user_id] >= 0 else 0
        if update.callback_query:
            context.bot.answer_callback_query(update.callback_query.id)
        index -= 2
        if index < 0:
            index = 0
        self.feedback[user_id] = self.feedback[user_id][:index]
        self.status_index[user_id] = index
        status = RATING_VALUES[index]
        self.status[user_id] = status
        logger.info(f"creo con index {index}")
        user_message = self.user_message[user_id]
        user_message = "\n\n".join(user_message.split("\n\n")[:-2])
        self.user_message[user_id] = user_message
        self.create_poll(f"{status}", chat_id, context)
        context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=self.message_id[user_id],
            text=self.user_message[user_id] + "\n\n\n<b>Dai un voto a...</b>",
            parse_mode="HTML",
        )
        return

    def cancel_rating(self, update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        self.status_index[user_id] = 0
        self.status[user_id] = RATING_VALUES[0]
        remove_commands(update, context)

    def deny_rating(self, update: Update, context: CallbackContext):
        message: Message = update.effective_message
        first_name = None
        if message.entities:
            entity = message.entities[0]
            try:
                first_name = entity['user']['first_name']
            except Exception as e:
                logger.error(e)
        callback = update.callback_query
        data = callback.data
        data = data.split("_")
        user_id = data[-1]
        code = data[-2]
        UserRating.objects(user_id=user_id, approved=True).delete()
        user_rating: UserRating = UserRating.objects.get(user_id=user_id, code=code)
        user = retrieve_user(user_id)
        if first_name:
            user.first_name = first_name
        text = build_approve_rating_message(user_rating, user)
        text = re.sub("\n\n\n.*$", "", text)
        user = update.effective_user
        date = datetime.now()
        date = date.strftime("%d/%m/%Y alle %H:%M")
        text += (
            "\n\n\n❌  <b>Non approvato da"
            f' <a href="tg://user?id={update.effective_user.id}">{update.effective_user.first_name}</a> in data {date}!</b>'
        )
        context.bot.edit_message_text(
            message_id=update.effective_message.message_id,
            text=text,
            chat_id=update.effective_chat.id,
            reply_markup=None,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
        user_rating.ui_comment = ""
        user_rating.ux_comment = ""
        user_rating.overall_comment = ""
        user_rating.functionality_comment = ""
        user_rating.approved = True
        user_rating.save()
        context.bot.send_message(
            chat_id=user_id,
            text=USER_MESSAGE_REVIEW_NOT_APPROVED_FROM_STAFF,
            reply_markup=RATING_REVIEWED_KEYBOARD,
            parse_mode="HTML",
        )
        self.calculate_weighted_average()

    def approve_rating(self, update: Update, context: CallbackContext):
        message: Message = update.effective_message
        first_name = None
        if message.entities:
            entity = message.entities[0]
            try:
                first_name = entity['user']['first_name']
            except Exception as e:
                logger.error(e)
        callback = update.callback_query
        data = callback.data
        data = data.split("_")
        user_id = data[-1]
        logger.info(f"approving {user_id}")
        code = data[-2]
        UserRating.objects(user_id=user_id, approved=True).delete()
        user_rating = UserRating.objects.get(user_id=user_id, code=code)
        user_rating.approved = True
        user_rating.save()
        user = retrieve_user(user_id)
        if first_name:
            user.first_name = first_name
        text = build_approve_rating_message(user_rating, user)
        user = update.effective_user
        text = re.sub("\n\n\n.*$", "", text)
        date = datetime.now()
        date = date.strftime("%d/%m/%Y alle %H:%M")
        text += (
            "\n\n\n✅  <b>Approvato da"
            f' <a href="tg://user?id={update.effective_user.id}">{update.effective_user.first_name}</a> in data {date}!</b>'
        )
        context.bot.edit_message_text(
            message_id=update.effective_message.message_id,
            text=text,
            chat_id=update.effective_chat.id,
            reply_markup=None,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
        context.bot.send_message(
            chat_id=user_id,
            text=USER_MESSAGE_REVIEW_APPROVED_FROM_STAFF,
            reply_markup=RATING_REVIEWED_KEYBOARD,
            parse_mode="HTML",
        )
        self.calculate_weighted_average()

    def delete_reviewed_rating_message(self, update: Update, context: CallbackContext):
        context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id,
        )

    def calculate_weighted_average(self):
        update_configuration = self.configuration_helper.update_configuration
        FULL_WEIGHT = 1
        HALF_WEIGHT = 0.25
        overall_votes = []
        overall_weights = []

        ui_votes = []
        ui_weights = []

        ux_votes = []
        ux_weights = []

        functionality_votes = []
        functionality_weights = []

        user_ratings: List[UserRating] = UserRating.objects.filter(approved=True)
        for user_rating in user_ratings:
            overall_votes.append(user_rating.overall_vote)
            weight = FULL_WEIGHT if user_rating.overall_comment else HALF_WEIGHT
            overall_weights.append(weight)

            ui_votes.append(user_rating.ui_vote)
            weight = FULL_WEIGHT if user_rating.ui_comment else HALF_WEIGHT
            ui_weights.append(weight)

            ux_votes.append(user_rating.ux_vote)
            weight = FULL_WEIGHT if user_rating.ux_comment else HALF_WEIGHT
            ux_weights.append(weight)

            functionality_votes.append(user_rating.functionality_vote)
            weight = FULL_WEIGHT if user_rating.functionality_comment else HALF_WEIGHT
            functionality_weights.append(weight)
        
        logger.info(f"OVERALL {overall_votes} {overall_weights}")
        logger.info(f"UI {ui_votes} {ui_weights}")
        logger.info(f"UX {ux_votes} {ux_weights}")
        logger.info(f"FUNC {functionality_votes} {functionality_weights}")

        overall_vote = np.average(overall_votes, weights=overall_weights)
        logger.info(f"OVERALL_VOTE {overall_vote}")
        update_configuration("overall_vote", str(overall_vote))
        ui_vote = np.average(ui_votes, weights=ui_weights)
        logger.info(f"UI_VOTE {ui_vote}")
        update_configuration("ui_vote", str(ui_vote))
        ux_vote = np.average(ux_votes, weights=ux_weights)
        logger.info(f"UX_VOTE {ux_vote}")
        update_configuration("ux_vote", str(ux_vote))
        functionality_vote = np.average(functionality_votes, weights=functionality_weights)
        logger.info(f"FUNCTIONALITY_VOTE {functionality_vote}")
        update_configuration("functionality_vote", str(functionality_vote))
        average = np.average([ui_vote, ux_vote, overall_vote, functionality_vote])
        logger.info(f"AVERAGE {average}")
        update_configuration("average_rating", str(average))