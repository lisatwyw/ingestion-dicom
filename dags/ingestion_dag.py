from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

from pathlib import Path
from glob import glob

import sys; sys.path.append('src')
from ingestion_pipeline import MultimodalIngestionPipeline

RAW_DIR = "/opt/airflow/data/raw"
SAFE_DIR = "/opt/airflow/data/safe"

pipeline = MultimodalIngestionPipeline(
    raw_data_dir=RAW_DIR,
    safe_data_dir=SAFE_DIR,
    secret_key=b"super-secret-key"
)

# -----------------------
# TASK FUNCTIONS
# -----------------------

def get_repo_root():
    # Airflow runs from /opt/airflow
    return Path.cwd()

def process_dicom_task():
    data_dir = get_repo_root() / "data"

    files = glob( data_dir / '*.dcm')
    for f in files:
        filename = data_dir / f  # later: from DB or file listing
        output = pipeline.process_dicom(filename)
        print(f"DICOM saved at: {output}")
    return output


def process_text_task():
    report_text = "John Doe visited Vancouver General Hospital on March 3rd."
    report_id = "report_001"
    output = pipeline.process_text_report(report_text, report_id)
    print(f"Report saved at: {output}")
    return output


# -----------------------
# DAG
# -----------------------

with DAG(
    dag_id="multimodal_ingestion",
    start_date=datetime(2026, 5, 1),
    schedule="@daily",
    catchup=False
) as dag:

    dicom_task = PythonOperator(
        task_id="process_dicom",
        python_callable=process_dicom_task,
    )

    text_task = PythonOperator(
        task_id="process_text",
        python_callable=process_text_task,
    )

    dicom_task >> text_task