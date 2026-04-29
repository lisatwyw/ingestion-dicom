FROM apache/airflow:2.9.1-python3.10

ENV PYTHONUNBUFFERED=1
ENV AIRFLOW_HOME=/opt/airflow

WORKDIR /opt/airflow

USER root
RUN apt-get update && apt-get install -y \
    build-essential gcc g++ curl && \
    apt-get clean

COPY requirements.txt .

USER airflow

RUN pip install --no-cache-dir -r requirements.txt

COPY dags/ /opt/airflow/dags/
COPY src/ /opt/airflow/src/

ENV PYTHONPATH=/opt/airflow/src

CMD ["airflow", "standalone"]