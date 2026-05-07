from fastapi import FastAPI, UploadFile, File
from backend.utils.file_handler import save_upload
from backend.routes import tender
from backend.routes import bidder
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def home():
    return {"message": "API running"}
app.include_router(tender.router, prefix="/tender")
app.include_router(bidder.router, prefix="/bidder")
