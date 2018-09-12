FROM python:3.6.5-slim

LABEL maintainer="Christian Kongsgaard <ocni@dtu.dk>" \
      description="RIBuild HPC Simulation Image"

WORKDIR /app

COPY ../delphin_6_automation /app

ENTRYPOINT ["python"]

CMD ["docker_simulation_hpc.py"]