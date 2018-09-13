FROM python:3.6.5-slim

LABEL maintainer="Christian Kongsgaard <ocni@dtu.dk>" \
      description="RIBuild HPC Simulation Image"

WORKDIR /app

ADD ../../delphin_6_automation /app
ADD ../../requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

CMD ["python", "docker_simulation_hpc.py"]