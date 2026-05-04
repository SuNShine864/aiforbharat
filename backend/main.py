from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import json
import tempfile
import os
from dotenv import load_dotenv

load_dotenv()

from extractors.document_extractor import extract_text_from_file
from extractors.criteria_extractor  import extract_criteria
from parsers.bid_parser             import parse_bids
from evaluators.verdict_engine      import run_evaluation

app = FastAPI(title="Tender Eval AI Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Health ─────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok"}

# ── Extract Criteria ───────────────────────────────────
# Input:  tender_file (PDF/DOCX), session_id
# Output: { criteria: [{id, description, type, mandatory, threshold, raw}] }
@app.post("/extract-criteria")
async def extract_criteria_endpoint(
    tender_file: UploadFile = File(...),
    session_id: str = Form(...)
):
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save uploaded file
        file_path = os.path.join(tmpdir, tender_file.filename)
        with open(file_path, "wb") as f:
            f.write(await tender_file.read())

        # Step 1: extract text (OCR if needed)
        text = extract_text_from_file(file_path)
        if not text.strip():
            raise HTTPException(400, "Could not extract text from tender document")

        # Step 2: send to LLM for criteria extraction
        criteria = extract_criteria(text)

    return {"criteria": criteria, "session_id": session_id}


# ── Evaluate Bids ──────────────────────────────────────
# Input:  session_id, criteria (JSON), bid_files (multiple)
# Output: { summary, bidders: [{id, name, overallVerdict, criteria:[...]}] }
@app.post("/evaluate")
async def evaluate_endpoint(
    session_id: str = Form(...),
    criteria: str = Form(...),    # JSON string
    bid_files: List[UploadFile] = File(default=[])
):
    criteria_list = json.loads(criteria)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Save all bid files
        saved_files = []
        for upload in bid_files:
            file_path = os.path.join(tmpdir, upload.filename)
            with open(file_path, "wb") as f:
                f.write(await upload.read())
            saved_files.append({"path": file_path, "name": upload.filename})

        # Step 1: extract text from each bid file
        bid_texts = []
        for file_info in saved_files:
            text = extract_text_from_file(file_info["path"])
            bid_texts.append({
                "filename": file_info["name"],
                "text": text,
                "ocr_used": False  # set by extractor
            })

        # Step 2: parse bids — group files by bidder, extract evidence per criterion
        parsed_bids = parse_bids(bid_texts, criteria_list)

        # Step 3: run verdict engine
        results = run_evaluation(parsed_bids, criteria_list)

    return results
