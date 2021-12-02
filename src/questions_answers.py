import os
import redis
import random

REDIS_URL = os.environ['REDIS_URL']
REDIS_PORT = os.environ['REDIS_PORT']
REDIS_DB = os.environ['REDIS_DB']
REDIS_PASSWORD = os.environ['REDIS_PASSWORD']
REDIS_CONNECTION = redis.Redis(host=REDIS_URL, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD)


def get_correct_answer(user_id, prefix):
    answer = REDIS_CONNECTION.get('{}-{}'.format(user_id, prefix))

    if answer is None:
        raise Exception('Ошибка получения вопроса для проверки ответа. Для следующего вопроса нажми "Новый вопрос"')

    return answer.decode('utf8')


def is_answer_correct(user_answer, answer):
    divider_index = answer.index('.')
    answer = answer[:divider_index]

    return user_answer.casefold() == answer.casefold()
