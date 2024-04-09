include .env

install:
	cd app && \
		poetry lock --no-update && \
		poetry install
