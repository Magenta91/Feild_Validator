from pydantic import BaseModel
from typing import Optional


class UploadConfig(BaseModel):
    country_code: str = "IN"
    date_format: str = "%Y-%m-%d"
    chunk_size: int = 1000
    split_output: bool = False


class ValidationSummary(BaseModel):
    worker: str
    is_valid: bool
    error_count: int
    errors: list


class ProcessResponse(BaseModel):
    success: bool
    message: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    validation_summaries: list[ValidationSummary]
    download_url: Optional[str] = None
    chunk_urls: Optional[list[str]] = None
