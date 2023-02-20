# syntax=docker/dockerfile:1
FROM python:3.11-bullseye

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
RUN python3 setup.py develop

RUN mkdir /var/log/shorthand
RUN mkdir -p /var/lib/shorthand/cache/

RUN mkdir /etc/shorthand
COPY sample_config.json /etc/shorthand/shorthand_config.json

CMD [ "python3", "-m" , "flask", "--app=shorthand/web/app", "run", "--host=0.0.0.0", "--port=8181"]
