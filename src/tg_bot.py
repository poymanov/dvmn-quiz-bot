from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
import os
import logging
import telegram
import questions_answers

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__file__)

NEW_QUESTION, SOLUTION_ATTEMPT, SURRENDER = range(3)


def send_message(context, user_id, text, reply_markup=None):
    context.bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup)


def error(update, context):
    logger.exception('Telegram-бот упал с ошибкой')


def handle_new_question_request(update, context):
    user_id = update.effective_chat.id

    question = questions_answers.add_question_to_user(user_id, 'tg')

    send_message(context, user_id, question)

    return SOLUTION_ATTEMPT


def handle_solution_attempt(update, context):
    user_id = update.effective_chat.id

    try:
        question = questions_answers.get_user_question(user_id, 'tg')
        answer = questions_answers.get_answer(question)

        if questions_answers.is_answer_correct(update.message.text, answer):
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
        question = questions_answers.get_user_question(user_id, 'tg')
        answer = questions_answers.get_answer(question)

        send_message(context, user_id, answer)

        new_question = questions_answers.add_question_to_user(user_id, 'tg')

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
