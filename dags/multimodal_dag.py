import pydicom
import numpy as np
import hashlib
from pathlib import Path

class MultimodalIngestionPipeline:
    def __init__(self, raw_data_dir, safe_data_dir, secret_key: bytes | None = None):
        self.raw_dir = Path(raw_data_dir)
        self.safe_dir = Path(safe_data_dir)
        self.safe_dir.mkdir(parents=True, exist_ok=True)
        self.secret_key = secret_key  # for HMAC-style pseudonymization

    def _pseudo_id(self, patient_id: str) -> str:
        """Stable, privacy-preserving identifier."""
        if self.secret_key:
            import hmac
            import hashlib
            return hmac.new(
                self.secret_key,
                patient_id.encode(),
                hashlib.sha256
            ).hexdigest()
        else:
            return hashlib.sha256(patient_id.encode()).hexdigest()

    def _anonymize_dicom(self, ds: pydicom.Dataset) -> pydicom.Dataset:
        """
        Lightweight DICOM de-identification using pydicom primitives.
        """

        # 1. Remove private tags (critical first step)
        ds.remove_private_tags()

        # 2. Remove direct identifiers
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

        # 3. Replace identifiers with safe placeholders
        ds.PatientName = "ANONYMIZED"
        ds.PatientID = "ANONYMIZED"

        return ds

    def process_dicom(self, filename: str) -> str:
        dicom_path = self.raw_dir / filename

        # 1. Load DICOM
        dataset = pydicom.dcmread(dicom_path)

        # 2. De-identify using structured approach
        dataset = self._anonymize_dicom(dataset)

        # 3. Extract pixel data safely
        raw_pixels = dataset.pixel_array.astype(np.float32)

        ptp = np.ptp(raw_pixels)
        if ptp == 0:
            normalized_pixels = np.zeros_like(raw_pixels)
        else:
            normalized_pixels = (raw_pixels - np.min(raw_pixels)) / ptp

        # 4. Safe metadata extraction (ONLY non-PHI)
        safe_metadata = {
            "Modality": dataset.get("Modality", "UNKNOWN"),
            "BodyPartExamined": dataset.get("BodyPartExamined", "UNKNOWN"),
            "Rows": dataset.get("Rows"),
            "Columns": dataset.get("Columns")
        }

        # 5. Stable pseudonymous file ID
        raw_pid = str(dataset.get("PatientID", filename))
        pseudo_id = self._pseudo_id(raw_pid)

        # 6. Save artifact
        output_file = self.safe_dir / f"img_{pseudo_id}.npy"
        np.save(output_file, normalized_pixels)

        return str(output_file)