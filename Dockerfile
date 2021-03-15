FROM node:14
WORKDIR /webapp/

COPY webapp/package.json .
COPY webapp/package-lock.json .
RUN npm install

COPY webapp/rollup.config.js .
COPY webapp/tsconfig.json .
COPY webapp/src ./src

RUN npm run build


FROM node:14
WORKDIR /email_builder/

COPY email_builder/package.json .
COPY email_builder/package-lock.json .
RUN npm install

COPY email_builder/src ./src
COPY email_builder/index.js .
RUN npm run build


FROM python:3.8
WORKDIR /django_bike/

COPY requirements.txt /django_bike/
RUN pip install -r requirements.txt

COPY django_bike/.env /django_bike/.env
COPY manage.py /django_bike/
COPY apps /django_bike/apps
COPY --from=0 /webapp/public/build /django_bike/webapp/public/build
COPY --from=1 /email_builder/build /django_bike/apps/main/templates/email
COPY start-server.sh /django_bike/
