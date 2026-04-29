# About

## Orchestration

### DAG for Dicom
- Pull DICOMs
- Extract pixel arrays with pydicom

```
[Ingest DICOMs]
    ↓
[Extract Pixel Data]
    ↓
[Normalize Images]
```

### DAG for reports
- De-identify reports
- Validate outputs
- Store in your training dataset

```
[Ingest Reports] → [De-identify Text]
    ↓
[Validate Data]
    ↓
[Store Dataset]
```

## Usage

```
pip install git+https://github.com/lisatwyw/ingestion-demo.git@main
```

```

from src.ingestion_pipeline import MultimodalIngestionPipeline

pipeline = MultimodalIngestionPipeline( 'data', 'test' )
out = pipeline.process_dicom( 'IMG-0001-00001.dcm' )

r = 'hello patient john doe seen at seatle on oct 12, 2023. mri shows mild osteroarthritis'
out2= pipeline.process_text_report(report_text = r, report_id='1111')

```

## Files
```
ingest-dicom/
├── src/
│   ├── __init__.py
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── dicom_processor.py
│   │   └── text_processor.py
│   └── utils/
│       ├── __init__.py
│       └── file_handlers.py
├── tests/
│   ├── test_dicom_normalization.py
│   └── test_phi_redaction.py
├── dags/
│   └── multimodal_dag.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
└── README.md
```

<details>

<summary></summary>

# a) unsafe:
```
pseudo_id = str(hash(dataset.get("PatientID", filename))) 
```

# b) safer but vulnerable to dictionary attack (hackable if someone brute-force small ID or know name of patient):
```      
import hashlib
pid = str(dataset.get("PatientID", filename)).encode()
pseudo_id = hashlib.sha256(pid).hexdigest()
```

# c) even safer: pseudonymization
```
pseudo_id = hashlib.sha256(pid).hexdigest()
```

# d) best practice: use HMAC (keyed hashing)

```
import hmac
pseudo_id = hmac.new(SECRET, pid, hashlib.sha256).hexdigest()
```
</details>