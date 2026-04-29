FROM python:3.12-slim

# Prevent Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Airflow home
ENV AIRFLOW_HOME=/opt/airflow

WORKDIR /opt/airflow

# System deps (needed for some Python packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && apt-get clean

# Copy requirements first (better caching)
COPY requirements.txt .

# Install Airflow with constraints (CRITICAL)
RUN pip install --no-cache-dir "apache-airflow==2.9.1" \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.1/constraints-3.11.txt"

# Install remaining deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Initialize Airflow DB
RUN airflow db init

# Default command
CMD ["airflow", "standalone"]