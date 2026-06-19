import os
import uuid
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from workers.ingestion_worker import IngestionWorker
from workers.phone_worker import PhoneWorker
from workers.date_worker import DateWorker
from workers.integrity_worker import IntegrityWorker
from workers.cleaner_worker import CleanerWorker
from workers.splitter_worker import SplitterWorker

app = FastAPI(
    title="Xeno Transaction Validator",
    description="Modular transaction data validation and processing platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use temp directory that works on both Unix and Windows
import tempfile
OUTPUT_DIR = os.path.join(tempfile.gettempdir(), "xeno_outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.get("/")
def root():
    return {"message": "Xeno Validator API is running", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/config/countries")
def get_supported_countries():
    from config.country_codes import COUNTRY_PHONE_RULES
    return {
        code: {"name": rules["name"], "digits": rules["digits"]}
        for code, rules in COUNTRY_PHONE_RULES.items()
    }


@app.get("/config/date-formats")
def get_supported_date_formats():
    from config.country_codes import SUPPORTED_DATE_FORMATS
    return {"supported_formats": SUPPORTED_DATE_FORMATS}


@app.post("/validate")
async def validate_file(
    file: UploadFile = File(...),
    country_code: str = Form(default="IN"),
    date_format: str = Form(default="%Y-%m-%d"),
    chunk_size: int = Form(default=1000),
    split_output: bool = Form(default=False)
):
    # ---- Step 1: Ingest ----
    ingestion = IngestionWorker()
    try:
        content = await file.read()
        df = ingestion.ingest(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if df.empty:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    stats = ingestion.get_stats()

    # ---- Step 2: Validate (polymorphic worker loop) ----
    validators = [
        PhoneWorker(),
        DateWorker(),
        IntegrityWorker(),
    ]

    validation_results = []
    for worker in validators:
        result = worker.validate(df, country_code=country_code, date_format=date_format)
        validation_results.append(result)

    # ---- Step 3: Clean and Prepare Reports ----
    cleaner = CleanerWorker()
    cleaned_df = cleaner.process(df, validation_results=validation_results)
    clean_summary = cleaner.get_summary()

    # Generate unique session ID for files
    session_id = uuid.uuid4().hex[:8]
    
    # ---- Generate Report Files ----
    # 1. Validation Report (all records with status)
    validation_report_df = df.copy()
    
    # Collect all error rows and their reasons
    error_map = {}  # {row_index: [error_reasons]}
    for result in validation_results:
        for error in result.errors:
            if error["row"] > 0:
                row_idx = error["row"] - 2
                if row_idx not in error_map:
                    error_map[row_idx] = []
                error_map[row_idx].append(error["reason"])
    
    # Add status and error_reason columns
    validation_report_df["status"] = validation_report_df.index.map(
        lambda i: "FAIL" if i in error_map else "PASS"
    )
    validation_report_df["error_reason"] = validation_report_df.index.map(
        lambda i: "; ".join(error_map[i]) if i in error_map else ""
    )
    
    validation_report_path = os.path.join(OUTPUT_DIR, f"validation_report_{session_id}.csv")
    validation_report_df.to_csv(validation_report_path, index=False)
    
    # 2. Failed Records (only failed records with errors)
    failed_df = validation_report_df[validation_report_df["status"] == "FAIL"].copy()
    failed_records_path = os.path.join(OUTPUT_DIR, f"failed_records_{session_id}.csv")
    failed_df.to_csv(failed_records_path, index=False)
    
    # 3. Cleaned CSV (valid records only - this is the existing cleaned_df)
    cleaned_csv_path = os.path.join(OUTPUT_DIR, f"cleaned_data_{session_id}.csv")
    cleaned_df.to_csv(cleaned_csv_path, index=False)

    # ---- Step 4: Split or Save (keeping existing functionality) ----
    splitter = SplitterWorker()
    splitter.process(
        cleaned_df,
        chunk_size=chunk_size,
        output_dir=OUTPUT_DIR
    )
    split_summary = splitter.get_summary()

    # ---- Build Response ----
    chunk_urls = [
        f"/download/{os.path.basename(path)}"
        for path in splitter.chunk_paths
    ]
    
    # Add new report URLs
    report_urls = {
        "validation_report": f"/download/validation_report_{session_id}.csv",
        "failed_records": f"/download/failed_records_{session_id}.csv",
        "cleaned_data": f"/download/cleaned_data_{session_id}.csv"
    }

    return JSONResponse({
        "success": True,
        "message": "Validation and processing complete",
        "file_stats": stats,
        "clean_summary": clean_summary,
        "split_summary": split_summary,
        "validation_summaries": [r.summary() for r in validation_results],
        "download_urls": chunk_urls,
        "report_urls": report_urls
    })


@app.get("/download/{filename}")
def download_file(filename: str):
    # Sanitise filename to prevent path traversal
    safe_name = os.path.basename(filename)
    file_path = os.path.join(OUTPUT_DIR, safe_name)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found or expired")

    return FileResponse(
        path=file_path,
        media_type="text/csv",
        filename=safe_name
    )
