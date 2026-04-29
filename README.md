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
