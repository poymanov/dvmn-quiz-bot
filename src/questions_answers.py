import os
import redis
import random

REDIS_URL = os.environ['REDIS_URL']
REDIS_PORT = os.environ['REDIS_PORT']
REDIS_DB = os.environ['REDIS_DB']
REDIS_PASSWORD = os.environ['REDIS_PASSWORD']
REDIS_CONNECTION = redis.Redis(host=REDIS_URL, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD)
QUESTIONS_PATH = os.environ['QUESTIONS_PATH']


def get_correct_answer(user_id, prefix):
    answer = REDIS_CONNECTION.get('{}-{}'.format(user_id, prefix))

    if answer is None:
        raise Exception('Ошибка получения вопроса для проверки ответа. Для следующего вопроса нажми "Новый вопрос"')

    return answer.decode('utf8')


def is_answer_correct(user_answer, answer):
    divider_index = answer.index('.')
    answer = answer[:divider_index]

    return user_answer.casefold() == answer.casefold()


def get_questions_answers():
    files = os.listdir(QUESTIONS_PATH)

    data = dict()

    for file in files:
        with open('{}/{}'.format(QUESTIONS_PATH, file), 'r', encoding='KOI8-R') as questions_file:
            line = questions_file.readline()

            is_question = False
            is_answer = False
            question = ''
            answer = ''

            while line:
                line = questions_file.readline()

                if 'Вопрос' in line:
                    question = ''
                    is_question = True
                    continue

                if 'Ответ' in line:
                    is_answer = True
                    answer = ''
                    continue

                if is_question:
                    if not line.strip():
                        is_question = False

                    question += ' ' + line.strip()

                if is_answer:
                    if not line.strip():
                        is_answer = False
                        data.update({question.strip(): answer.strip()})

                    answer += ' ' + line.strip()

    return data
