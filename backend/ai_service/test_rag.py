import os
import json

from extractors.document_extractor import (
    extract_text_from_file
)

from rag_pipeline import (
    index_bidder_chunks,
    retrieve_relevant_chunks,
    evaluate_criterion
)

# =========================
# SAMPLE PDF
# =========================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

pdf_path = os.path.join(

    BASE_DIR,

    "data",

    "samples",
    "mmrc",
    "bidder",
    "xyz_enterprises_pvt_lmtd_bid.pdf"
)

# =========================
# EXTRACT TEXT
# =========================

print("\n=== EXTRACTING TEXT ===\n")

blocks = extract_text_from_file(
    pdf_path
)

for b in blocks:

    b["filename"] = "sample_bidder.pdf"

print(json.dumps(

    blocks,

    indent=2,

    ensure_ascii=False
))

# =========================
# INDEX CHUNKS
# =========================

print("\n=== INDEXING ===\n")

bidder_id = "TEST_BIDDER"

index_bidder_chunks(

    bidder_id,

    blocks
)

# =========================
# TEST CRITERION
# =========================

criterion = {

    "id": "C001",

    "category": "financial",

    "description": (
        "Average annual turnover "
        "must exceed ₹5 Crore"
    )
}

# =========================
# RETRIEVE RELEVANT CHUNKS
# =========================

print("\n=== RETRIEVING ===\n")

chunks = retrieve_relevant_chunks(

    bidder_id,

    criterion["description"],

    top_k=5
)

print(json.dumps(

    chunks,

    indent=2,

    ensure_ascii=False
))

# =========================
# NVIDIA EVALUATION
# =========================

print("\n=== NVIDIA EVALUATION ===\n")

result = evaluate_criterion(

    criterion,

    chunks
)

print(json.dumps(

    result,

    indent=2,

    ensure_ascii=False
))