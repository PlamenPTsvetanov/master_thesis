FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
COPY src ./src

RUN mkdir resources
RUN mkdir resources/videos
RUN mkdir resources/frames


RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "python src/kafka/VideoCreatedKafkaConsumer.py && tail -f /dev/null"]
