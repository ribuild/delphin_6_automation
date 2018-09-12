FROM python:3.6.5-slim

LABEL maintainer="Christian Kongsgaard <ocni@dtu.dk>" \
      description="RIBuild Sampling Image"

WORKDIR /app

COPY ../../delphin_6_automation /app
COPY ../../requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

CMD ["python", "docker_sampling.py"]