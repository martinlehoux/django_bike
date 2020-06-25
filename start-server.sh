while ! curl http://db:5432/ 2>&1 | grep '52'
do
  sleep 1
done
python manage.py migrate
python manage.py collectstatic --no-input --clear
python manage.py runserver 0.0.0.0:8000
# gunicorn django_bike.wsgi:application --bind 0.0.0.0:8000
