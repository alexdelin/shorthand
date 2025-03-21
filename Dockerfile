# syntax=docker/dockerfile:1
FROM python:3.12-bullseye

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
RUN python3 setup.py develop

RUN mkdir /var/log/shorthand
RUN mkdir -p /var/lib/shorthand/cache/

RUN mkdir /etc/shorthand
COPY sample_config.json /etc/shorthand/shorthand_config.json
RUN cp test/config_override.json.docker test/config_override.json

RUN mkdir /notes
COPY sample-notes /notes

CMD [ "fastapi", "run", "shorthand/web/app-fastapi.py", "--port=8181"]
