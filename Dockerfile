# Use an official Python base image
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY src .

# Command to run the Kafka consumer
CMD ["python", "consumer.py"]
