![Django CI](https://github.com/martinlehoux/django_bike/workflows/Django%20CI/badge.svg)
[![Website bike.lehoux.net](https://img.shields.io/website-up-down-green-red/http/bike.lehoux.net.svg)](https://bike.lehoux.net)

## Installation

### Production

**Update**

```bash
git pull
docker-compose up -d --no-deps --build db flower redis web worker
```

### Development

**Create python environment**

- `python3 -m venv env`
- `source env/bin/activate`
- `pip install -r requirements.txt`

**Configure project**
- `cp django_bikes/template.env django_bikes/.env`
- Edit this new file and fill the required values.
  - `USE_CACHE` enable cache when filled with any value
  - `SITE_NAME` used for displaying the site name
  - `POSTGRES_PASSWORD` is not required in development mode (using SQLite3)
  - `SENDGRID_KEY` is not required in development mode (using Maildev). See https://sendgrid.com/.
  - `SECRET_KEY` can be generated using python : 
    ```python3
    >>> from django.core.management.utils import get_random_secret_key
    >>> get_random_secret_key()
    ```

**Build the webapp**
- `cd webapp`
- `npm i`
- `npm run build`

**Build the email**
- `cd email_builder`
- `npm i`
- `npm run build`

**Start the server**
- `./manage.py createsuperuser`
- `./manage.py migrate`
- `./manage.py runserver`

Many side tools are used in this project. You should have a working docker install to be able to use them.

**Redis**
Redis is used as a message queue for notifications and for worker actions. It is also used for caching.
To run: `docker run -p 6379:6379 redis`

**Celery worker**
A celery worker performs slow background actions, such as parsing GPX files.
Depends on: **redis**
To run: `celery -A django_bike worker --loglevel=info`

**Maildev**
Maildev is a local mail SMTP and client to test sending emails locally.
You can see your mail box at http://0.0.0.0:1081
To run: `docker run -p 1081:80 -p 25:25 maildev/maildev`

### Releasing a new version

- `poetry version major|minor|patch`
- Write `release-notes/x.y.z.yml` release note with the **correct date**.
- Create a PR

### Options

**Flower**
Flower helps you monitor you workers and your Redis messages. The site will work the same if not activated.
Depends on: **redis**
To run: `celery flower -A django_bike`


### References
- http://www.movable-type.co.uk/scripts/latlong.html
- https://github.com/tkrajina/gpxpy
- https://github.com/tkrajina/srtm.py