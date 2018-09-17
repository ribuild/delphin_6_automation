FROM python:3.7.0-alpine

LABEL maintainer="Christian Kongsgaard <ocni@dtu.dk>" \
      description="RIBuild Python Base Image"

WORKDIR /app

ADD ././delphin_6_automation /app/delphin_6_automation
ADD ././requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

RUN mkdir /app/data