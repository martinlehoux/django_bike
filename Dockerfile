FROM python:3.8
WORKDIR /django_bike/
ENV SERVER_TYPE stage

COPY requirements.txt /django_bike/
RUN pip install -r requirements.txt

COPY django_bike/.env /django_bike/.env
COPY manage.py /django_bike/
COPY start-server.sh /django_bike/
