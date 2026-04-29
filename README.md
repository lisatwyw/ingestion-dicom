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
