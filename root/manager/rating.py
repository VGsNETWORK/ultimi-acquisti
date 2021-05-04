#!/usr/bin/env python3


from datetime import datetime

from telegram.callbackquery import CallbackQuery
from root.helper.user_helper import create_user, retrieve_user
from telegram.message import Message
from telegram.user import User
from root.model.user_rating import UserRating
from root.util.util import create_button, retrieve_key
from root.manager.start import rating_cancelled, remove_commands
from root.contants.keyboard import (
    RAITING_KEYBOARD,
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
    build_approve_rating_message,
    build_show_rating_message,
)
from uuid import uuid4
import root.util.logger as logger
import re


class Rating:
    def __init__(self):
        self.status_index = {}
        self.status = {}
        self.feedback = {}
        self.message_id = {}
        self.user_message = {}

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
        log_channel = retrieve_key("ERROR_CHANNEL")
        user_rating: UserRating = UserRating(
            approve_message_id=0,
            approve_chat_id=log_channel,
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
            chat_id=log_channel,
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
        user_id = update.effective_user.id
        if not user_id in self.status_index:
            return
        if self.status_index[user_id] == 0:
            return
        logger.info("ricevuto feedback")
        chat_id = update.effective_chat.id
        message_id = update.effective_message.message_id
        if not update.callback_query:
            text = f'"{update.effective_message.text}"'
        else:
            text = "<b>Non presente</b>"
        index = self.status_index[user_id] if self.status_index[user_id] >= 0 else 0
        vote = self.feedback[user_id][index - 1]["vote"]
        vote = vote * "⭐️"
        if self.status_index[user_id] == 1:
            self.user_message[
                user_id
            ] = f"{RATING_VALUES[index - 1]}:  {vote}\nCommento:  <i>{text}</i>"
        else:
            self.user_message[user_id] += f"\nCommento:  <i>{text}</i>"
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
                            "start_hide_commands",
                            "start_hide_commands",
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
        message = context.bot.send_poll(
            chat_id,
            text,
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
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        message_id = update.effective_message.message_id
        approved = UserRating.objects.filter(user_id=user_id, approved=True)
        to_approve = UserRating.objects.filter(user_id=user_id, approved=False)
        if approved or to_approve:
            message = USER_ALREADY_VOTED
            if approved:
                approved_message = f"<b>{len(approved)}</b> recensione pubblicata (✅)"
                approved = approved[0]
            else:
                approved_message = ""
            if to_approve:
                to_approve_message = (
                    f"<b>{len(to_approve)}</b> recensione in fase di valutazione (⚖️)"
                )
                to_approve = to_approve[0]
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

        context.bot.edit_message_text(
            chat_id=chat_id,
            text=message,
            message_id=message_id,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=build_pre_poll_keyboard(approved, to_approve),
        )

    def show_rating(self, update: Update, context: CallbackContext):
        """ Show user rating """
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        message_id = update.effective_message.message_id
        callback: CallbackQuery = update.callback_query
        code = callback.data
        code = code.split("_")[-1]
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
        if self.user_message[user_id]:
            text = f"\n\n{status}:  {stars}"
        else:
            text = f"{status}:  {stars}"
        self.user_message[user_id] += text
        context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=self.message_id[user_id],
            text=self.user_message[user_id] + "\n\n\n<b>Inserisci un commento:</b>",
            reply_markup=InlineKeyboardMarkup(RAITING_KEYBOARD),
            parse_mode="HTML",
        )
        self.status[user_id] = RATING_VALUES[self.status_index[user_id]]
        context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        self.status_index[user_id] += 1

    def cancel_rating(self, update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        self.status_index[user_id] = 0
        self.status[user_id] = RATING_VALUES[0]
        remove_commands(update, context)

    def deny_rating(self, update: Update, context: CallbackContext):
        callback = update.callback_query
        data = callback.data
        data = data.split("_")
        user_id = data[-1]
        code = data[-2]
        user_rating = UserRating.objects.get(user_id=user_id, code=code)
        user = retrieve_user(user_id)
        text = build_approve_rating_message(user_rating, user)
        text = re.sub("\n\n\n.*$", "", text)
        user = update.effective_user
        date = datetime.now()
        date = date.strftime("%d/%m/%Y alle %H:%M")
        text += (
            "\n\n\n❌  <b>Non approvato da"
            f' <a href="tg://user?id={user.id}">{user.first_name}</a> in data {date}!</b>'
        )
        context.bot.edit_message_text(
            message_id=update.effective_message.message_id,
            text=text,
            chat_id=update.effective_chat.id,
            reply_markup=None,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
        user_rating.delete()

    def approve_rating(self, update: Update, context: CallbackContext):
        callback = update.callback_query
        data = callback.data
        data = data.split("_")
        user_id = data[-1]
        code = data[-2]
        UserRating.objects(user_id=user_id, approved=True).delete()
        user_rating = UserRating.objects.get(user_id=user_id, code=code)
        user_rating.approved = True
        user_rating.save()
        user = retrieve_user(user_id)
        text = build_approve_rating_message(user_rating, user)
        user = update.effective_user
        text = re.sub("\n\n\n.*$", "", text)
        date = datetime.now()
        date = date.strftime("%d/%m/%Y alle %H:%M")
        text += (
            "\n\n\n✅  <b>Approvato da"
            f' <a href="tg://user?id={user.id}">{user.first_name}</a> in data {date}!</b>'
        )
        context.bot.edit_message_text(
            message_id=update.effective_message.message_id,
            text=text,
            chat_id=update.effective_chat.id,
            reply_markup=None,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
