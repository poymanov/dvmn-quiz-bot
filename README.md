# Бот для проведения викторин

Репозиторий содержит боты для Telegram и группы ВК, которые проводят викторины и задают вопросы пользователям. В случае если пользователь не знает ответа на вопрос, он может сдаться и увидеть правильный ответ.

Пример для Telegram:

![](docs/demo_tg_bot.gif)

Пример для VK:

![](docs/demo_vk_bot.gif)

[Демо-бот в Telegram](https://t.me/poymanov_dvmn_quiz_bot)

[Демо-группа с ботом в VK](https://vk.com/club209075987)

### Установка

Для работы приложения требуется **Docker** и **Docker Compose**.

Для инициализации приложения выполнить команду:

```
make init
```

### Настройка

Разместить в директории `questions` вопросы с ответами (примеры формата файлов в директории `examples`).

В файле `.env` заполнить:

|Параметр|Описание |
|-----------|-----------|
|*TELEGRAM_BOT_TOKEN*|Токен бота поддержки в Telegram|
|*VK_GROUP_TOKEN*|Токен бота поддержки в VK|
|*REDIS_URL*|URL базы в Redis (можно использовать [Redis Labs](https://app.redislabs.com)|
|*REDIS_PORT*|Порт базы в Redis|
|*REDIS_PASSWORD*|Пароль базы в Redis|
|*REDIS_DB*|Номер базы в Redis|

### Запуск

Telegram бот:

```
make tg-bot 
```

Бот группы VK:

```
make vk-bot
```

Удаление всех временных файлов приложения:

```
make flush
```

### Цель проекта

Код написан в образовательных целях на онлайн-курсе [dvmn.org](https://dvmn.org/), в рамках
модуля [Чат-боты на Python](https://dvmn.org/modules/chat-bots).