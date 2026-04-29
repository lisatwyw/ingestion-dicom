from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

from pathlib import Path
from glob import glob
import logging
import sys

# Make src importable
sys.path.append("/opt/airflow/src")

from ingestion_pipeline import MultimodalIngestionPipeline


# -----------------------
# STARTUP MESSAGE (visible in logs on parse)
# -----------------------
print("\n" + "=" * 60)
print("🚀 Multimodal Ingestion DAG Loaded")
print("=" * 60 + "\n")

logging.info("DAG multimodal_ingestion loaded successfully")


# -----------------------
# HELPERS
# -----------------------
def get_repo_root():
    # Inside Docker / Codespaces
    return Path("/opt/airflow")


# -----------------------
# TASKS
# -----------------------
def process_dicom_task():
    pipeline = MultimodalIngestionPipeline()

    data_dir = get_repo_root() / "data"
    files = glob(str(data_dir / "*.dcm"))

    if not files:
        print("⚠️ No DICOM files found in data/")
        return []

    outputs = []

    for f in files:
        file_path = Path(f)

        output = pipeline.process_dicom(file_path)

        print(f"✅ Processed {file_path} -> {output}")
        outputs.append(str(output))

    return outputs


def process_text_task():
    pipeline = MultimodalIngestionPipeline()

    report_text = "John Doe visited Vancouver General Hospital on March 3rd."
    report_id = "report_001"

    output = pipeline.process_text_report(report_text, report_id)

    print(f"📄 Text report saved at: {output}")
    return str(output)


# -----------------------
# DAG DEFINITION
# -----------------------
with DAG(
    dag_id="multimodal_ingestion",
    start_date=datetime(2026, 5, 1),
    schedule="@daily",
    catchup=False,
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