FROM ribuild_base:latest

LABEL maintainer="Christian Kongsgaard <ocni@dtu.dk>" \
      description="RIBuild HPC Simulation Image"

WORKDIR /app

ADD ././delphin_6_automation /app/delphin_6_automation

VOLUME /app/data

WORKDIR /app/delphin_6_automation

CMD ["python", "docker_simulation_hpc.py"]