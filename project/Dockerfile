# pull official base image
FROM python:3.11.8-slim

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update \
    && apt-get -y install netcat-traditional gcc postgresql \
    && apt-get clean

# install python dependencies
COPY ./pyproject.toml .
RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install 

# add 
COPY . .

# add entrypoint.sh
COPY ./entrypoint.sh .
RUN chmod +x /usr/src/app/entrypoint.sh

# run entrypoint.sh
# ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
