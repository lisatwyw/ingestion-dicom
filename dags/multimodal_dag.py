
import pydicom
import numpy as np
import spacy
import json
import os
from pathlib import Path

'''
Demo: Standard spacy model 

In production: use 
- en_ner_bionlp13cg_md
- Spark NLP for Healthcare
- AWS Comprehend Medical

'''

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

class MultimodalIngestionPipeline:
    def __init__(self, raw_data_dir, safe_data_dir):
        self.raw_dir = Path(raw_data_dir)
        self.safe_dir = Path(safe_data_dir)
        self.safe_dir.mkdir(parents=True, exist_ok=True)

    def process_dicom(self, filename: str) -> str:
        """Extracts pixels, normalizes, and strips PHI metadata."""
        dicom_path = self.raw_dir / filename
        
        # 1. Read the raw DICOM file
        dataset = pydicom.dcmread(dicom_path)
        
        # 2. Extract and perform intensity-normalization
        #    Pixel Array (Min-Max Scaling)
        raw_pixels = dataset.pixel_array.astype(float)
        normalized_pixels = (raw_pixels - np.min(raw_pixels)) / (np.max(raw_pixels) - np.min(raw_pixels))
        
        # 3. Extract ONLY safe metadata (to avoid PHI)
        safe_metadata = {
            "Modality": dataset.get("Modality", "UNKNOWN"),
            "BodyPartExamined": dataset.get("BodyPartExamined", "UNKNOWN"),
            "Rows": dataset.get("Rows"),
            "Columns": dataset.get("Columns")
        }
        
        # 4. Save to safe environment (NumPy format for ML training)
        # Using a hash or UUID instead of PatientID for the filename
        pseudo_id = str(hash(dataset.get("PatientID", filename))) 
        output_file = self.safe_dir / f"img_{pseudo_id}.npy"
        np.save(output_file, normalized_pixels)
        
        return str(output_file)

    def process_text_report(self, report_text: str, report_id: str) -> str:
        """Applies NER to remove PHI and stores in a structured JSON format."""
        
        # 1. Run NER for De-identification
        doc = nlp(report_text)
        clean_text = report_text
        
        # Entities to redact (Names, Dates, Locations, Organizations)
        phi_labels = {"PERSON", "DATE", "ORG", "GPE", "LOC"}
        
        for ent in doc.ents:
            if ent.label_ in phi_labels:
                # Replace PHI with its entity type tag
                clean_text = clean_text.replace(ent.text, f"[{ent.label_}]")
                
        # 2. Format for structured store
        structured_data = {
            "report_id": report_id,
            "processed_length": len(clean_text),
            "clean_findings": clean_text
        }
        
        # 3. Save to safe environment
        output_file = self.safe_dir / f"report_{report_id}.json"
        with open(output_file, 'w') as f:
            json.dump(structured_data, f, indent=4)
            
        return str(output_file)

# Example
if __name__ == "__main__":
    pipeline = MultimodalIngestionPipeline(raw_data_dir="./landing_zone", safe_data_dir="./dev_environment")
    
    # Example 1: Text De-identification in action
    raw_report = "Patient John Doe was seen at Seattle Grace Hospital on October 12th, 2023. MRI shows mild osteoarthritis."
    safe_path = pipeline.process_text_report(raw_report, report_id="1001")
    
    print("Processing Complete. De-identified text payload:")
    with open(safe_path, 'r') as f:
        print(f.read())