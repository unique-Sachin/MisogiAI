# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1 \
    PINECONE_ENVIRONMENT=us-east1-gcp \
    PINECONE_INDEX_NAME=financial-intel-index \
    PINECONE_DIMENSION=1024

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 