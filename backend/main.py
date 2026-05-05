from fastapi import FastAPI, UploadFile, File
from backend.utils.file_handler import save_upload
from backend.routes import tender
from backend.routes import bidder

app = FastAPI()
@app.get("/")
def home():
    return {"message": "API running"}
app.include_router(tender.router, prefix="/tender")
app.include_router(bidder.router, prefix="/bidder")
