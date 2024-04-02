FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

# USER root

# ENV VIRTUAL_ENV /workspaces/.venv
# ENV PATH /workspaces/.venv/bin:${PATH}

RUN apt-get update && \
    apt-get install iputils-ping -y

RUN pip install pip --upgrade && \
    pip install poetry ignr

WORKDIR /workspaces
COPY . .

# RUN make install


