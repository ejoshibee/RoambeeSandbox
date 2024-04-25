FROM python:3.12-slim-bookworm

# Set unbuffer env for print logging
ENV PYTHONUNBUFFERED=1

# Install gcc and g++ for stupid dependencies. TODO: DEP CLEANUP
RUN apt-get update && apt-get install -y cron
RUN apt-get install -y gcc  && apt-get install -y g++
RUN pip install --upgrade pip uv 

# Set an app directory
WORKDIR /ConfluenceRag

# Copy requirements.txt to the app directory
COPY requirements.txt /ConfluenceRag/requirements.txt


# Install dependencies
RUN uv pip install --system --requirement /ConfluenceRag/requirements.txt

COPY . /ConfluenceRag

ENV $(cat .env | xargs)

# Expose the port
EXPOSE 8501

# COPY crontab crontab
# RUN chmod 0644 crontab

# RUN crontab crontab
# RUN touch /tmp/out.log

# Run the Streamlit app
CMD ["streamlit", "run", "main.py"]