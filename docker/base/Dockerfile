FROM python:3.6.3-slim

LABEL maintainer="Christian Kongsgaard <ocni@dtu.dk>" \
      description="RIBuild Python Base Image"

WORKDIR /app

ADD ././requirements.txt /app/requirements.txt

RUN pip --no-cache-dir install -r requirements.txt

RUN mkdir /app/data