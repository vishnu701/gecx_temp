FROM python:3.10-slim-buster

ENV PYENV_SHELL=/bin/bash

ENV GOOGLE_APPLICATION_CREDENTIALS=secrets/gecx.json

RUN set -ex; \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends build-essential && \
    pip install --no-cache-dir --upgrade pip && \
    pip install pipenv && \
    mkdir -p /app

WORKDIR /app

ADD Pipfile Pipfile.lock /app/

RUN pipenv sync

ADD . /app

EXPOSE 8000

CMD ["pipenv", "run", "uvicorn", "cli:app", "--host", "0.0.0.0", "--port", "8000"]
