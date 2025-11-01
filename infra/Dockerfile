# /infra/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all our application code
COPY ./model /app/model
COPY ./service /app/service

# Expose the API port
EXPOSE 8000

# Default command is to run the API
CMD ["uvicorn", "service.main:app", "--host", "0.0.0.0", "--port", "8000"]