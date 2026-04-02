FROM python:3.12-slim

ENV POETRY_VERSION=2.1.4 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    PYTHONPATH=/notification_service

WORKDIR /notification_service

ARG gitlab_ssh_key

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-client \
    git \
    make \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip3 install --no-cache-dir "poetry==$POETRY_VERSION"

RUN poetry install --only=main --no-interaction --no-ansi --no-root

RUN apt-get remove -y --purge gcc python3-dev && \
    apt-get autoremove -y --purge && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* ~/.cache/pip ~/.cache/pypoetry

RUN rm -f ~/.ssh/id_rsa
