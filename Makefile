include .env

p:
	echo ${SONAR_LOCALHOST_TOKEN}

install:
	cd app && \
		poetry lock --no-update && \
		poetry install
