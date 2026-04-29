# Use a slim Python base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies (sometimes needed for specific DICOM compressions)
RUN apt-get update && apt-get install -y gcc libgdcm-tools && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download the spaCy model during the build step, NOT at runtime
RUN python -m spacy download en_core_web_sm

# Copy the pipeline code
COPY ingestion_pipeline.py .

# Command to execute the pipeline (or start an Airflow worker)
CMD ["python", "ingestion_pipeline.py"]
