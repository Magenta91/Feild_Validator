from datetime import datetime
from pandas import DataFrame
from base.base_validator import BaseValidator
from models.validation_result import ValidationResult
from config.country_codes import SUPPORTED_DATE_FORMATS


class DateWorker(BaseValidator):
    """
    Validates date and datetime fields against predefined formats.
    Tries all supported formats and flags anything that doesn't match.
    """

    def __init__(self):
        super().__init__(worker_name="DateWorker")

    def validate(self, df: DataFrame, date_format: str = "%Y-%m-%d", **kwargs) -> ValidationResult:
        result = self._init_result(df)
        date_cols = self._detect_date_columns(df)

        if not date_cols:
            return result  # No date columns found, skip silently

        for col in date_cols:
            for idx, row in df.iterrows():
                raw_value = str(row[col]).strip()

                if raw_value in ("", "nan", "None", "NaT"):
                    result.add_error(
                        row=idx + 2, column=col,
                        value=raw_value,
                        reason="Date field is empty or null"
                    )
                    continue

                parsed = self._try_parse(raw_value, date_format)

                if parsed is None:
                    result.add_error(
                        row=idx + 2, column=col,
                        value=raw_value,
                        reason=f"Could not parse date. Expected format: {date_format}. "
                               f"Tried all supported formats: {SUPPORTED_DATE_FORMATS}"
                    )
                    result.cleaned_df.at[idx, col] = None
                else:
                    # Standardise to YYYY-MM-DD
                    result.cleaned_df.at[idx, col] = parsed.strftime("%Y-%m-%d")

        self._result = result
        return result

    def _try_parse(self, value: str, preferred_format: str):
        """Try preferred format first, then fall back to all supported formats."""
        formats_to_try = [preferred_format] + [
            f for f in SUPPORTED_DATE_FORMATS if f != preferred_format
        ]
        for fmt in formats_to_try:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        return None

    def _detect_date_columns(self, df: DataFrame) -> list:
        date_keywords = ["date", "time", "dt", "created", "updated", "timestamp", "ordered_at"]
        return [col for col in df.columns if any(kw in col.lower() for kw in date_keywords)]

    def get_error_report(self) -> list:
        if self._result is None:
            return []
        return self._result.errors
