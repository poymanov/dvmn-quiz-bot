tg-bot:
	docker-compose run --rm app python src/tg_bot.py

vk-bot:
	docker-compose run --rm app python src/vk_bot.py

flush:
	docker-compose down -v --rmi all

build:
	docker-compose build

init:
	cp .env.example .env