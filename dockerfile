# Use ubuntu as our base
FROM ubuntu:focal AS build

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
ARG SSH_USERNAME
ARG SSH_PASSWORD
ARG SSH_KEY
ARG RESULT_PATH
ARG BIN_PATH
ARG WEBGUI_PATH
ENV SSH_USERNAME="example_user"
ENV SSH_PASSWORD="example_pass"
ENV SSH_KEY="/app/ssh_id"
ENV RESULT_PATH="/app/result_files"
ENV BIN_PATH="/app/bin"
ENV WEBGUI_PATH="/app/webcontent"

# Update and install some packages
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y python3-pip git curl
RUN pip3 install "fastapi[all]" "uvicorn[standard]" python-dotenv paramiko argparse pingparsing jinja2

# Copy the files into the proper app directory
COPY api-server /app/api-server
COPY bin /app/bin
RUN mkdir -p /app/result_files
WORKDIR /app/api-server
VOLUME /app/result_files

# Define the basic healthcheck of the container
# Interval        = Interval of when the command is run from container start
# Timeout         = Check should take no longer than this
# Start Period    = Time for container to "get its legs", ignore fails in this time
# Retries         = Number of times a fail needs to trigger unhealthy
HEALTHCHECK  --interval=1m --timeout=3s --start-period=15s --retries=3  CMD curl --fail http://localhost:9180/ || exit 1

#CMD  ["uvicorn", "main:app", "--reload" ]
CMD  ["python3", "/app/api-server/main.py"]
