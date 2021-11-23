import os
import logging
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

VK_GROUP_TOKEN = os.environ['VK_GROUP_TOKEN']

logger = logging.getLogger(__file__)


def echo(event, vk_api):
    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('Новый вопрос')
    keyboard.add_button('Сдаться')

    keyboard.add_line()
    keyboard.add_button('Мой счёт')

    vk_api.messages.send(
        user_id=event.user_id,
        message=event.text,
        keyboard=keyboard.get_keyboard(),
        random_id=get_random_id()
    )


def main():
    vk_session = vk.VkApi(token=VK_GROUP_TOKEN)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            echo(event, vk_api)


if __name__ == '__main__':
    main()
