FROM python:3.11-bookworm

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
COPY dist/pt_deepfake_finder-0.1.0-py3-none-any.whl /app/dist/pt_deepfake_finder-0.1.0-py3-none-any.whl
#COPY dist/best_model.h5 /app/src/input/
COPY src/input/haarcascade_frontalface_default.xml /src/input/

RUN pip install --no-cache-dir dist/pt_deepfake_finder-0.1.0-py3-none-any.whl
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

RUN mkdir -p resources/videos resources/frames

ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "python src/Gateway.py && tail -f /dev/null"]
