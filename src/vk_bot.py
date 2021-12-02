import os
import logging
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
import questions_answers
import random
from data import get_questions_and_answers

VK_GROUP_TOKEN = os.environ['VK_GROUP_TOKEN']

logger = logging.getLogger(__file__)


def handle_new_question_request(event, vk_api):
    user_id = event.user_id
    question = random.choice(list(get_questions_and_answers().items()))

    questions_answers.REDIS_CONNECTION.set('{}-{}'.format(user_id, 'vk'), question[1])
    send_message(vk_api, user_id, question[0])


def handle_solution_attempt(event, vk_api):
    user_id = event.user_id

    correct_answer = questions_answers.get_correct_answer(user_id, 'vk')

    if questions_answers.is_answer_correct(event.text, correct_answer):
        send_message(vk_api, user_id, 'Правильно! Поздравляю! Для следующего вопроса нажми "Новый вопрос".')
    else:
        send_message(vk_api, user_id, 'Неправильно… Попробуешь ещё раз?')


def handle_surrender(event, vk_api):
    user_id = event.user_id

    correct_answer = questions_answers.get_correct_answer(user_id, 'vk')

    send_message(vk_api, user_id, correct_answer)

    question = random.choice(list(get_questions_and_answers().items()))
    questions_answers.REDIS_CONNECTION.set('{}-{}'.format(user_id, 'vk'), question[1])

    send_message(vk_api, user_id, question[0])


def get_keyboard():
    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)

    keyboard.add_line()
    keyboard.add_button('Мой счёт')

    return keyboard.get_keyboard()


def send_message(vk_api, user_id, message):
    vk_api.messages.send(
        user_id=user_id,
        message=message,
        keyboard=get_keyboard(),
        random_id=get_random_id()
    )


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    vk_session = vk.VkApi(token=VK_GROUP_TOKEN)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            try:
                if event.text == 'Новый вопрос':
                    handle_new_question_request(event, vk_api)
                elif event.text == 'Сдаться':
                    handle_surrender(event, vk_api)
                else:
                    handle_solution_attempt(event, vk_api)
            except Exception as e:
                send_message(vk_api, event.user_id, 'Возникла ошибка. Мы уже работаем над её исправлением.')
                logger.exception()


if __name__ == '__main__':
    main()
