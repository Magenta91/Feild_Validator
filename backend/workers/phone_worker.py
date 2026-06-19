import re
from pandas import DataFrame
from base.base_validator import BaseValidator
from models.validation_result import ValidationResult
from config.country_codes import COUNTRY_PHONE_RULES


class PhoneWorker(BaseValidator):
    """
    Validates phone numbers based on country-specific rules.
    Rules are driven by configurable country codes from config/country_codes.py.
    """

    def __init__(self):
        super().__init__(worker_name="PhoneWorker")

    def validate(self, df: DataFrame, country_code: str = "IN", **kwargs) -> ValidationResult:
        result = self._init_result(df)

        if country_code not in COUNTRY_PHONE_RULES:
            result.add_error(
                row=-1, column="config",
                value=country_code,
                reason=f"Unsupported country code '{country_code}'. Supported: {list(COUNTRY_PHONE_RULES.keys())}"
            )
            return result

        rules = COUNTRY_PHONE_RULES[country_code]
        phone_col = self._detect_phone_column(df)

        if phone_col is None:
            result.add_error(
                row=-1, column="schema",
                value="N/A",
                reason="No phone number column detected in dataset"
            )
            return result

        # Ensure phone column is string type to allow mixed assignments
        result.cleaned_df[phone_col] = result.cleaned_df[phone_col].astype(object)

        for idx, row in df.iterrows():
            raw_value = str(row[phone_col]).strip()
            cleaned = re.sub(r"[\s\-\(\)\+]", "", raw_value)

            # Check digit count
            if not cleaned.isdigit():
                result.add_error(
                    row=idx + 2, column=phone_col,
                    value=raw_value,
                    reason="Phone number contains non-numeric characters"
                )
                result.cleaned_df.at[idx, phone_col] = None
                continue

            if len(cleaned) != rules["digits"]:
                result.add_error(
                    row=idx + 2, column=phone_col,
                    value=raw_value,
                    reason=f"Expected {rules['digits']} digits for {rules['name']}, got {len(cleaned)}"
                )
                result.cleaned_df.at[idx, phone_col] = None
                continue

            # Check valid prefix
            if rules["prefix_required"] and rules["prefixes"]:
                if cleaned[0] not in rules["prefixes"]:
                    result.add_error(
                        row=idx + 2, column=phone_col,
                        value=raw_value,
                        reason=f"Invalid prefix '{cleaned[0]}' for {rules['name']}. Valid: {rules['prefixes']}"
                    )
                    result.cleaned_df.at[idx, phone_col] = None
                    continue

            # Valid — store cleaned version
            result.cleaned_df.at[idx, phone_col] = cleaned

        self._result = result
        return result

    def _detect_phone_column(self, df: DataFrame):
        phone_keywords = ["phone", "mobile", "contact", "number", "ph_no", "phone_number"]
        for col in df.columns:
            if any(kw in col.lower() for kw in phone_keywords):
                return col
        return None

    def get_error_report(self) -> list:
        if self._result is None:
            return []
        return self._result.errors
