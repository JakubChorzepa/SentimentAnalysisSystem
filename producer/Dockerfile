FROM python:3.12-slim

ENV DOCKER_ENV=true

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .

CMD ["python", "-u", "app.py"]