FROM python:3.13-bookworm

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

RUN mkdir -p resources/videos resources/frames

ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

CMD ["python", "src/Gateway.py"]
