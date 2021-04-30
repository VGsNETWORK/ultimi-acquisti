#!/usr/bin/env python3


from root.util.util import create_button
from root.manager.start import rating_cancelled, remove_commands
from root.contants.keyboard import RAITING_KEYBOARD
from telegram.ext.callbackcontext import CallbackContext
from telegram.error import BadRequest
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.update import Update
from root.contants.messages import RATING_PLACEHOLDER, RATING_VALUES
import root.util.logger as logger


class Rating:
    def __init__(self):
        self.status_index = {}
        self.status = {}
        self.feedback = {}
        self.message_id = {}
        self.user_message = {}

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
            text = f"<i>{status}:</i>  {stars}"
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
