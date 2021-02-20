# Containers
redis:
	docker run -p 6379:6379 redis

worker:
	celery -A django_bike worker --loglevel=info

flower:
	celery flower -A django_bike

maildev:
	docker run -p 1081:80 -p 25:25 maildev/maildev

# Utils
lint:
	poetry run isort .
	poetry run black .
	poetry run flake8

test:
	poetry run pytest apps

docker-stop:
	docker ps -q | xargs docker kill

docker-build-restart:
	docker-compose up --build --force-recreate -d

docker-webapp:
	docker build -t django_bike/webapp -f Dockerfile.webapp .
	docker run --rm -v ${PWD}/webapp/public/build:/webapp/public/build -t django_bike/webapp

export:
	poetry export -f requirements.txt -o requirements.txt --without-hashes
