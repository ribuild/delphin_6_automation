FROM ribuild_base:latest

LABEL maintainer="Christian Kongsgaard <ocni@dtu.dk>" \
      description="RIBuild HPC Simulation Image"

WORKDIR /app

ADD ././delphin_6_automation /app/delphin_6_automation

VOLUME /app/data

WORKDIR /app/delphin_6_automation

RUN sed -i "s/server {/server {n n  error_log syslog_server=loggly;n    access_log syslog_server=loggly;n/" /app/delphin_6_automation/delphin_6_automation.log
CMD ["python", "docker_simulation_hpc.py"]