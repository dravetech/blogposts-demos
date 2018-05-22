FROM python:3.6

RUN pip install nornir flask

COPY . /monit

ENTRYPOINT python /monit/monit.py
