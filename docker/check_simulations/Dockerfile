FROM ocni/ribuild_base:latest

LABEL maintainer="Christian Kongsgaard <ocni@dtu.dk>" \
      description="RIBuild Check HPC Simulation Image"

WORKDIR /app

ADD ././delphin_6_automation /app/delphin_6_automation

WORKDIR /app/delphin_6_automation

CMD ["python", "check_running_simulations.py"]