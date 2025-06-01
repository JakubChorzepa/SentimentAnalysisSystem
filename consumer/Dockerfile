FROM python:3.12-slim

ENV DOCKER_ENV=true

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
COPY kafka_consumer.py kafka_consumer.py
COPY postgres_client.py postgres_client.py
COPY sentiment_analyzer.py sentiment_analyzer.py


CMD ["python", "-u", "app.py"]