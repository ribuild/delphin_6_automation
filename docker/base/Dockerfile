FROM python:3.7.0-slim

LABEL maintainer="Christian Kongsgaard <ocni@dtu.dk>" \
      description="RIBuild Python Base Image"

WORKDIR /app

ADD ././requirements.txt /app/requirements_docker.txt

RUN pip install -r requirements_docker.txt

RUN mkdir /app/data