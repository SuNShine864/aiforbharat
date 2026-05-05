# test_pipeline.py
import json 
import os
from extractors.document_extractor import extract_text_from_file
from extractors.criteria_extractor import extract_criteria
from parsers.bid_parser             import parse_bids
from evaluators.verdict_engine import run_evaluation
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
bidder_file_path = os.path.join(
    BASE_DIR, "data", "samples", "sample_bidder.pdf"
)
tender_file_path = os.path.join(
    BASE_DIR, "data", "samples", "sample.pdf"
)

print("\n[STEP 1] Extracting tender text...")
text = extract_text_from_file(tender_file_path)
print(text)

print("\n[STEP 2] Extracting criteria...")
criteria = extract_criteria(text)
print(json.dumps(criteria, indent=2,ensure_ascii=False))
print(criteria)
os.makedirs("outputs", exist_ok=True)  # create folder if not exists
with open("outputs/criteria.json", "w",encoding="utf-8") as f:
    json.dump(criteria, f, indent=2,ensure_ascii=False)
print("Criteria saved to criteria.json")

print("\n[STEP 3] Extracting bidder documents...")
bidder_blocks = extract_text_from_file(bidder_file_path)
print(bidder_blocks)
bidder_filename = os.path.basename(bidder_file_path)
bid_texts = [
    {
        "filename": bidder_filename,
        "text": bidder_blocks,
        "ocr_used": False
    }
]
print("\n[STEP 4] Parsing bidder...")
parsed_bids = parse_bids(bid_texts, criteria)
print("\n===== PARSED BIDS =====")
print(json.dumps(parsed_bids, indent=2,ensure_ascii=False))

print("\n[STEP 5] Running evaluation...")
results = run_evaluation(parsed_bids, criteria)
print("\n===== FINAL RESULTS =====")
print(json.dumps(results, indent=2,ensure_ascii=False))

print("\n Pipeline completed successfully")