ENV = /Users/mlehoux/.virtualenv/django-bike-gzBAQnCM-py3.8
lint:
	$(ENV)/bin/black django_bike apps

redis:
	docker run -p 6379:6379 redis

worker:
	celery -A django_bike worker --loglevel=info

flower:
	celery flower -A django_bike

docker-stop:
	docker ps -q | xargs docker kill

export:
	poetry export -f requirements.txt -o requirements.txt --without-hashes
