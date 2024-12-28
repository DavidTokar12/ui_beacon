FROM mcr.microsoft.com/devcontainers/python:3.12
ARG DEBIAN_FRONTEND=noninteractive
ARG USER=vscode

RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        libxml2-utils

RUN curl -sSL https://install.python-poetry.org | python3 -
