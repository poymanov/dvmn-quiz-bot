from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
import os
import logging
import telegram
import questions_answers
import random

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
QUESTIONS = questions_answers.get_questions_answers()

logger = logging.getLogger(__file__)

NEW_QUESTION, SOLUTION_ATTEMPT, SURRENDER = range(3)


def error(update, context):
    logger.exception('Telegram-бот упал с ошибкой')


def handle_new_question_request(update, context):
    user_id = update.effective_chat.id

    question, answer = random.choice(list(QUESTIONS.items()))
    questions_answers.REDIS_CONNECTION.set('{}-{}'.format(user_id, 'tg'), answer)

    context.bot.send_message(chat_id=user_id, text=question)

    return SOLUTION_ATTEMPT


def handle_solution_attempt(update, context):
    user_id = update.effective_chat.id

    correct_answer = questions_answers.get_correct_answer(user_id, 'tg')

    if questions_answers.is_answer_correct(update.message.text, correct_answer):
        context.bot.send_message(chat_id=user_id,
                                 text='Правильно! Поздравляю! Для следующего вопроса нажми "Новый вопрос".')

        return NEW_QUESTION
    else:
        context.bot.send_message(chat_id=user_id, text='Неправильно… Попробуешь ещё раз?')

        return SURRENDER


def handle_surrender(update, context):
    user_id = update.effective_chat.id

    correct_answer = questions_answers.get_correct_answer(user_id, 'tg')
    context.bot.send_message(chat_id=user_id, text=correct_answer)

    question, answer = random.choice(list(QUESTIONS.items()))
    questions_answers.REDIS_CONNECTION.set('{}-{}'.format(user_id, 'tg'), answer)

    context.bot.send_message(chat_id=user_id, text=question)


def start(update, context):
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счёт']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я бот для викторин!",
                             reply_markup=reply_markup)

    return NEW_QUESTION


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

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
