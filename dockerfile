# Use ubuntu as our base
FROM ubuntu:latest AS build

# Update and install some packages
RUN apt-get update && \
    apt-get upgrade -y && \
    apt autoremove -y 
RUN apt-get install -y python3-pip git curl libffi-dev python3-setuptools python-setuptools
RUN pip3 install -U pip
RUN pip3 install --upgrade setuptools
RUN pip3 install --upgrade "fastapi[all]" "uvicorn[standard]" python-dotenv paramiko argparse pingparsing jinja2 slowapi


# Some information labels
LABEL version=10001
LABEL org.opencontainers.image.authors="MindlessTux"
LABEL org.opencontainers.image.url=https://github.com/mindlesstux/my_looking_glass
LABEL org.opencontainers.image.documentation=https://github.com/mindlesstux/my_looking_glass
LABEL org.opencontainers.image.source=https://github.com/mindlesstux/my_looking_glass
LABEL org.opencontainers.image.version=10001
LABEL org.opencontainers.image.title="My Looking Glass"
LABEL org.opencontainers.image.description="This is a 'looking glass' application"

# We need this port,
EXPOSE 9180

# Build out the OS environmental variables
ARG BASE_PATH
ARG RESULT_PATH
ARG BIN_PATH
ARG WEBGUI_PATH
ARG HEALTH_CRON
ARG CAPABILITIES_DEFAULT
ARG CONFIGJSON_PATH
ENV BASE_PATH="/app"
#ENV RESULT_PATH="/app/result_files"
#ENV BIN_PATH="/app/bin"
#ENV WEBGUI_PATH="/app/webinterface"
#ENV CONFIGJSON_PATH="/app/config.json"
ENV HEALTH_CRON=15
ENV CAPABILITIES_DEFAULT='true'

# Copy the files into the proper app directory
COPY api-server /app/api-server
COPY bin /app/bin
COPY webinterface /app/webinterface
RUN mkdir -p /app/result_files
WORKDIR /app/api-server
VOLUME /app/result_files

# Define the basic healthcheck of the container
# Interval        = Interval of when the command is run from container start
# Timeout         = Check should take no longer than this
# Start Period    = Time for container to "get its legs", ignore fails in this time
# Retries         = Number of times a fail needs to trigger unhealthy
HEALTHCHECK  --interval=1m --timeout=3s --start-period=15s --retries=3  CMD curl --silent --output /dev/null --fail http://localhost:9180/healthcheck || exit 1

#CMD  ["uvicorn", "main:app", "--reload" ]
CMD  ["python3", "/app/api-server/main.py"]
