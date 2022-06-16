FROM ubuntu:focal AS build

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y python3-pip git
RUN pip3 install "fastapi[all]" "uvicorn[standard]" python-dotenv

# Grab latest master branch
RUN git clone https://github.com/mindlesstux/my_looking_glass.git /app
WORKDIR /app/api-server
VOLUME /app_data

#CMD  ["uvicorn", "main:app", "--reload" ]
CMD  ["python3", "/app/api-server/main.py"]
EXPOSE 9180