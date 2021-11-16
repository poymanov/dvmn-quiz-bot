from data import get_questions_and_answers
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os
import logging
import telegram
import redis

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
REDIS_URL = os.environ['REDIS_URL']
REDIS_PORT = os.environ['REDIS_PORT']
REDIS_DB = os.environ['REDIS_DB']
REDIS_PASSWORD = os.environ['REDIS_PASSWORD']

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__file__)
redisConnection = redis.Redis(host=REDIS_URL, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD)


def error(update, context):
    logger.exception('Telegram-бот упал с ошибкой')


def menu_command(update, context):
    user_id = update.effective_chat.id
    first_question = list(get_questions_and_answers())[0]

    if update.message.text == 'Новый вопрос':
        context.bot.send_message(chat_id=user_id, text=first_question)
        redisConnection.set(user_id, first_question)
        print(redisConnection.get(user_id).decode('utf8'))


def start_command(update, context):
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счёт']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я бот для викторин!",
                             reply_markup=reply_markup)


def main():
    updater = Updater(token=TELEGRAM_BOT_TOKEN)

    dispatcher = updater.dispatcher
    updater.start_polling()

    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), menu_command))
    dispatcher.add_handler(CommandHandler('start', start_command))
    dispatcher.add_error_handler(error)


if __name__ == '__main__':
    main()
