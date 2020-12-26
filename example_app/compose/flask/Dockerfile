FROM python:3.7-slim as dev

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN pip install --upgrade pip && pip install -r /requirements.txt --no-cache-dir

RUN groupadd -r flask && useradd -r -g flask flask

COPY --chown=flask . /app
WORKDIR /app
