ENV = /home/kagamino/.cache/pypoetry/virtualenvs/django-bike-AGosmyMN-py3.8

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
	$(ENV)/bin/black django_bike apps

test:
	SERVER_TYPE=test $(ENV)/bin/pytest apps

docker-stop:
	docker ps -q | xargs docker kill

docker-build-restart:
	docker-compose up --build --force-recreate -d

docker-webapp:
	docker build -t django_bike/webapp -f Dockerfile.webapp .
	docker run --rm -v ${PWD}/webapp/public/build:/webapp/public/build -t django_bike/webapp

export:
	poetry export -f requirements.txt -o requirements.txt --without-hashes

# Production
update:
	git pull
	docker-compose up -d --no-deps --build db flower redis web worker

logs:
	docker-compose logs -f --tail=10
