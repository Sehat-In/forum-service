FROM python:3.9

WORKDIR /code

ARG DATABASE_HOST
ARG DATABASE_NAME
ARG DATABASE_PORT
ARG DATABASE_USER
ARG DATABASE_PASSWORD
ARG RABBITMQ_SERVER
ARG RABBITMQ_USERNAME
ARG RABBITMQ_PASSWORD

ENV DATABASE_HOST ${DATABASE_HOST}
ENV DATABASE_NAME ${DATABASE_NAME}
ENV DATABASE_PORT ${DATABASE_PORT}
ENV DATABASE_USER ${DATABASE_USER}
ENV DATABASE_PASSWORD ${DATABASE_PASSWORD}
ENV RABBITMQ_SERVER ${RABBITMQ_SERVER}
ENV RABBITMQ_USERNAME ${RABBITMQ_USERNAME}
ENV RABBITMQ_PASSWORD ${RABBITMQ_PASSWORD}

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .

EXPOSE 3003

CMD ["fastapi", "run", "main.py", "--port", "3003"]