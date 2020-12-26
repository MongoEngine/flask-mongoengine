FROM python:3.7-slim as dev

ENV PYTHONUNBUFFERED 1
RUN groupadd -r flask && useradd -r -g flask flask
COPY --chown=flask . /flask_mongoengine
RUN pip install --upgrade pip && pip install -r /flask_mongoengine/requirements.txt && pip install -e /flask_mongoengine
WORKDIR /flask_mongoengine
