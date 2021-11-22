from data import get_questions_and_answers
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
import os
import logging
import telegram
import redis
import random

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
REDIS_URL = os.environ['REDIS_URL']
REDIS_PORT = os.environ['REDIS_PORT']
REDIS_DB = os.environ['REDIS_DB']
REDIS_PASSWORD = os.environ['REDIS_PASSWORD']

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__file__)
redisConnection = redis.Redis(host=REDIS_URL, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD)

NEW_QUESTION, SOLUTION_ATTEMPT, SURRENDER = range(3)


def send_message(context, user_id, text, reply_markup=None):
    context.bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup)


def add_question_to_user(user_id):
    question = random.choice(list(get_questions_and_answers().keys()))
    redisConnection.set(user_id, question)

    return question


def is_answer_correct(user_answer, answer):
    divider_index = answer.index('.')
    answer = answer[:divider_index]

    return user_answer.casefold() == answer.casefold()


def get_user_question(user_id):
    question = redisConnection.get(user_id)

    if question is None:
        raise Exception('Ошибка получения вопроса для проверки ответа. Для следующего вопроса нажми "Новый вопрос"')

    return question.decode('utf8')


def get_answer(question):
    questions_and_answers = get_questions_and_answers()

    if question not in questions_and_answers:
        raise Exception('Ошибка получения ответа на вопрос. Для следующего вопроса нажми "Новый вопрос"')

    return get_questions_and_answers()[question]


def error(update, context):
    logger.exception('Telegram-бот упал с ошибкой')


def handle_new_question_request(update, context):
    user_id = update.effective_chat.id

    question = add_question_to_user(user_id)

    send_message(context, user_id, question)

    return SOLUTION_ATTEMPT


def handle_solution_attempt(update, context):
    user_id = update.effective_chat.id

    try:
        question = get_user_question(user_id)
        answer = get_answer(question)

        if is_answer_correct(update.message.text, answer):
            send_message(context, user_id, 'Правильно! Поздравляю! Для следующего вопроса нажми "Новый вопрос".')

            return NEW_QUESTION
        else:
            send_message(context, user_id, 'Неправильно… Попробуешь ещё раз?')

            return SURRENDER
    except Exception as e:
        send_message(context, user_id, str(e))

        return NEW_QUESTION


def handle_surrender(update, context):
    user_id = update.effective_chat.id

    try:
        question = get_user_question(user_id)
        answer = get_answer(question)

        send_message(context, user_id, answer)

        new_question = add_question_to_user(user_id)

        send_message(context, user_id, new_question)
    except Exception as e:
        send_message(context, user_id, str(e))

    return SOLUTION_ATTEMPT


def start(update, context):
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счёт']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    send_message(context, update.effective_chat.id, "Привет! Я бот для викторин!", reply_markup)

    return NEW_QUESTION


def main():
    updater = Updater(token=TELEGRAM_BOT_TOKEN)

    dispatcher = updater.dispatcher

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            NEW_QUESTION: [MessageHandler(Filters.regex('^Новый вопрос$'), handle_new_question_request)],
            SURRENDER: [MessageHandler(Filters.regex('^Сдаться$'), handle_surrender),
                        MessageHandler(Filters.text, handle_solution_attempt)],
            SOLUTION_ATTEMPT: [MessageHandler(Filters.text, handle_solution_attempt)],
        },

        fallbacks=[]
    )

    dispatcher.add_handler(conversation_handler)
    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
