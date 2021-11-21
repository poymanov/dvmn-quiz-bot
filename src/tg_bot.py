from data import get_questions_and_answers
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
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


def send_message(context, user_id, text, reply_markup=None):
    context.bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup)


def is_answer_correct(user_answer, answer):
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

    raw_answer = get_questions_and_answers()[question]
    divider_index = raw_answer.index('.')
    return raw_answer[:divider_index]


def error(update, context):
    logger.exception('Telegram-бот упал с ошибкой')


def menu_command(update, context):
    user_id = update.effective_chat.id

    if update.message.text == 'Новый вопрос':
        question = random.choice(list(get_questions_and_answers().keys()))
        redisConnection.set(user_id, question)
        context.bot.send_message(chat_id=user_id, text=question)
    else:
        try:
            question = get_user_question(user_id)
            answer = get_answer(question)

            if is_answer_correct(update.message.text, answer):
                return send_message(context, user_id,
                                    'Правильно! Поздравляю! Для следующего вопроса нажми "Новый вопрос".')
            else:
                return send_message(context, user_id, 'Неправильно… Попробуешь ещё раз?')
        except Exception as e:
            send_message(context, user_id, str(e))


def start_command(update, context):
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счёт']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    send_message(context, update.effective_chat.id, "Привет! Я бот для викторин!", reply_markup)


def main():
    updater = Updater(token=TELEGRAM_BOT_TOKEN)

    dispatcher = updater.dispatcher
    updater.start_polling()

    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), menu_command))
    dispatcher.add_handler(CommandHandler('start', start_command))
    dispatcher.add_error_handler(error)


if __name__ == '__main__':
    main()
