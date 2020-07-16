FROM node:12
WORKDIR /webapp/

COPY webapp/package.json .
COPY webapp/package-lock.json .
RUN npm install

COPY webapp/rollup.config.js .
COPY webapp/tsconfig.json .
COPY webapp/src ./src

RUN [ "npm", "run", "build" ]


FROM python:3.8
WORKDIR /django_bike/
ENV SERVER_TYPE stage

COPY requirements.txt /django_bike/
RUN pip install -r requirements.txt

COPY django_bike/.env /django_bike/.env
COPY manage.py /django_bike/
COPY --from=0 /webapp/public/build /django_bike/webapp/public/build
COPY start-server.sh /django_bike/
