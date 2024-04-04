FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

RUN apt-get update && \
    apt-get install iputils-ping -y

RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

RUN . "/usr/local/share/nvm/nvm.sh" && nvm install 20

RUN pip install pip --upgrade && \
    pip install poetry ignr