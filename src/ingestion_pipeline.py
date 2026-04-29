
import json
from pathlib import Path
import pydicom
# Assumes spaCy model is loaded externally:
# In a production setting, you'd use a specialized clinical model 
# like en_ner_bionlp13cg_md, Spark NLP for Healthcare, or AWS Comprehend Medical.
# We load a standard spacy model here for demonstration.


class MultimodalIngestionPipeline:
    def __init__(self, raw_data_dir, safe_data_dir, secret_key: bytes | None = None):
        self.raw_dir = Path(raw_data_dir)
        self.safe_dir = Path(safe_data_dir)
        self.safe_dir.mkdir(parents=True, exist_ok=True)
        self.secret_key = secret_key

    def _load_nlp( self ):
        try:
            import spacy 
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            import spacy.cli
            spacy.cli.download("en_core_web_sm")
            nlp = spacy.load("en_core_web_sm")
        return nlp

    # -------------------------
    # ID PSEUDONYMIZATION
    # -------------------------
    def _pseudo_id(self, patient_id: str) -> str:
        """Stable, privacy-preserving identifier (HMAC if key exists)."""

        import hashlib
        import hmac

        if self.secret_key:
            return hmac.new(
                self.secret_key,
                patient_id.encode(),
                hashlib.sha256
            ).hexdigest()

        return hashlib.sha256(patient_id.encode()).hexdigest()

    # -------------------------
    # DICOM ANONYMIZATION
    # -------------------------
    def _anonymize_dicom(self, ds: pydicom.Dataset) -> pydicom.Dataset:
        """Basic DICOM de-identification (non-compliant but practical baseline)."""

        
        ds.remove_private_tags()

        sensitive_tags = [
            "PatientName",
            "PatientID",
            "PatientBirthDate",
            "PatientAddress",
            "PatientSex",
            "InstitutionName",
            "ReferringPhysicianName",
        ]

        for tag in sensitive_tags:
            if tag in ds:
                del ds[tag]

        # Hard overwrite safety layer
        ds.PatientName = "ANONYMIZED"
        ds.PatientID = "ANONYMIZED"

        return ds

    # -------------------------
    # DICOM PIPELINE
    # -------------------------
    def process_dicom(self, filename: str) -> str:
            
        import numpy as np

        dicom_path = self.raw_dir / filename

        dataset = pydicom.dcmread(dicom_path)
        dataset = self._anonymize_dicom(dataset)

        raw_pixels = dataset.pixel_array.astype(np.float32)

        # Stable normalization
        ptp = np.ptp(raw_pixels)
        normalized_pixels = (raw_pixels - raw_pixels.min()) / (ptp + 1e-8)

        safe_metadata = {
            "Modality": dataset.get("Modality", "UNKNOWN"),
            "BodyPartExamined": dataset.get("BodyPartExamined", "UNKNOWN"),
            "Rows": dataset.get("Rows"),
            "Columns": dataset.get("Columns")
        }

        raw_pid = str(dataset.get("PatientID", filename))
        pseudo_id = self._pseudo_id(raw_pid)

        output_file = self.safe_dir / f"img_{pseudo_id}.npy"
        np.save(output_file, normalized_pixels)

        return str(output_file)

    # -------------------------
    # TEXT PIPELINE (FIXED)
    # -------------------------
    def _redact_spans(self, doc, labels: set[str]) -> str:
        """Correct span-based redaction (no string replace bugs)."""

        chunks = []
        last_idx = 0

        
        for ent in doc.ents:
            if ent.label_ in labels:
                chunks.append(doc.text[last_idx:ent.start_char])
                chunks.append(f"[{ent.label_}]")
                last_idx = ent.end_char

        chunks.append(doc.text[last_idx:])
        return "".join(chunks)

    def process_text_report(self, report_text: str, report_id: str) -> str:
        """NER-based PHI redaction with structured output."""

        #doc = nlp(report_text)
        doc = self._load_nlp()( report_text )

        phi_labels = {"PERSON", "DATE", "ORG", "GPE", "LOC"}
        clean_text = self._redact_spans(doc, phi_labels)

        structured_data = {
            "report_id": report_id,
            "original_length": len(report_text),
            "clean_length": len(clean_text),
            "clean_findings": clean_text,
            "phi_entity_count": len(doc.ents),
        }

        output_file = self.safe_dir / f"report_{report_id}.json"

        with open(output_file, "w") as f:
            json.dump(structured_data, f, indent=2)

        return str(output_file)