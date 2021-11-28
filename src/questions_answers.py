import os
import redis
import random
from data import get_questions_and_answers

REDIS_URL = os.environ['REDIS_URL']
REDIS_PORT = os.environ['REDIS_PORT']
REDIS_DB = os.environ['REDIS_DB']
REDIS_PASSWORD = os.environ['REDIS_PASSWORD']
REDIS_CONNECTION = redis.Redis(host=REDIS_URL, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD)


def add_question_to_user(user_id, prefix):
    question = random.choice(list(get_questions_and_answers().keys()))
    REDIS_CONNECTION.set('{}-{}'.format(user_id, prefix), question)

    return question


def is_answer_correct(user_answer, answer):
    divider_index = answer.index('.')
    answer = answer[:divider_index]

    return user_answer.casefold() == answer.casefold()


def get_user_question(user_id, prefix):
    question = REDIS_CONNECTION.get('{}-{}'.format(user_id, prefix))

    if question is None:
        raise Exception('Ошибка получения вопроса для проверки ответа. Для следующего вопроса нажми "Новый вопрос"')

    return question.decode('utf8')


def get_answer(question):
    questions_and_answers = get_questions_and_answers()

    if question not in questions_and_answers:
        raise Exception('Ошибка получения ответа на вопрос. Для следующего вопроса нажми "Новый вопрос"')

    return get_questions_and_answers()[question]
