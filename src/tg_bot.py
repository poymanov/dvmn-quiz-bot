from data import get_questions_and_answers
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os
import logging

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__file__)


def error(update, context):
    logger.exception('Telegram-бот упал с ошибкой')


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def main():
    updater = Updater(token=TELEGRAM_BOT_TOKEN)

    dispatcher = updater.dispatcher
    updater.start_polling()

    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), echo))
    dispatcher.add_error_handler(error)


if __name__ == '__main__':
    main()
