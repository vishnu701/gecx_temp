FROM python:3.10-slim-buster

ENV PYENV_SHELL=/bin/bash

ENV GOOGLE_APPLICATION_CREDENTIALS=secrets/gecx.json

RUN set -ex; \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get -y install git && \
    apt-get install -y --no-install-recommends build-essential manpages-dev&& \
    pip install --no-cache-dir --upgrade pip && \
    pip install pipenv && \
    mkdir -p /app

WORKDIR /app

RUN gcc -v

ADD Pipfile Pipfile.lock /app/

RUN pipenv sync

ADD . /app

RUN pip install --upgrade setuptools wheel

RUN pipenv install -r /app/llama.cpp/requirements.txt

# RUN pip install llama_cpp_python

ENTRYPOINT ["/bin/bash"]

CMD ["-c", "pipenv shell"]