FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1
ENV CHROMADB_PORT=8000

COPY conftest.py .

ADD crontab /etc/cron.d/hello-cron

RUN apt-get update && apt-get install -y cron
RUN pip install chromadb

RUN chmod 0644 /etc/cron.d/hello-cron
RUN touch /var/log/cronjob.log
RUN crontab /etc/cron.d/hello-cron

CMD cron && tail -f /var/log/cronjob.log