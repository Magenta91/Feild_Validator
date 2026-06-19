from pandas import DataFrame
from base.base_validator import BaseValidator
from models.validation_result import ValidationResult
from config.country_codes import VALID_PAYMENT_MODES


class IntegrityWorker(BaseValidator):
    """
    Validates general data integrity:
    - Null/empty checks on critical fields
    - Duplicate row detection
    - Payment mode validation
    - Amount/numeric field checks
    - General format checks
    """

    def __init__(self):
        super().__init__(worker_name="IntegrityWorker")

    def validate(self, df: DataFrame, **kwargs) -> ValidationResult:
        result = self._init_result(df)

        self._check_nulls(df, result)
        self._check_duplicates(df, result)
        self._check_payment_mode(df, result)
        self._check_numeric_fields(df, result)
        self._check_email_format(df, result)

        self._result = result
        return result

    def _check_nulls(self, df: DataFrame, result: ValidationResult):
        critical_cols = self._get_critical_columns(df)
        for col in critical_cols:
            null_rows = df[df[col].isnull() | (df[col].astype(str).str.strip() == "")]
            for idx in null_rows.index:
                result.add_error(
                    row=idx + 2, column=col,
                    value="NULL",
                    reason=f"Critical field '{col}' is empty or null"
                )

    def _check_duplicates(self, df: DataFrame, result: ValidationResult):
        id_col = self._detect_id_column(df)
        if id_col is None:
            return
        duplicates = df[df.duplicated(subset=[id_col], keep=False)]
        for idx in duplicates.index:
            result.add_error(
                row=idx + 2, column=id_col,
                value=str(df.at[idx, id_col]),
                reason=f"Duplicate value found in ID column '{id_col}'"
            )

    def _check_payment_mode(self, df: DataFrame, result: ValidationResult):
        payment_col = self._detect_column(df, ["payment_mode", "payment", "pay_mode", "payment_method"])
        if payment_col is None:
            return
        for idx, row in df.iterrows():
            val = str(row[payment_col]).strip().lower()
            if val not in ("nan", "none", "") and val not in VALID_PAYMENT_MODES:
                result.add_error(
                    row=idx + 2, column=payment_col,
                    value=val,
                    reason=f"Invalid payment mode '{val}'. Valid: {VALID_PAYMENT_MODES}"
                )

    def _check_numeric_fields(self, df: DataFrame, result: ValidationResult):
        numeric_keywords = ["amount", "price", "qty", "quantity", "total", "cost"]
        for col in df.columns:
            if any(kw in col.lower() for kw in numeric_keywords):
                for idx, row in df.iterrows():
                    val = str(row[col]).strip()
                    if val in ("nan", "none", ""):
                        continue
                    try:
                        num = float(val)
                        if num < 0:
                            result.add_error(
                                row=idx + 2, column=col,
                                value=val,
                                reason=f"Numeric field '{col}' cannot be negative"
                            )
                    except ValueError:
                        result.add_error(
                            row=idx + 2, column=col,
                            value=val,
                            reason=f"Field '{col}' expected numeric value, got '{val}'"
                        )

    def _check_email_format(self, df: DataFrame, result: ValidationResult):
        email_col = self._detect_column(df, ["email", "email_id", "mail"])
        if email_col is None:
            return
        for idx, row in df.iterrows():
            val = str(row[email_col]).strip()
            
            # Flag missing/empty emails as errors
            if val in ("nan", "none", ""):
                result.add_error(
                    row=idx + 2, column=email_col,
                    value="EMPTY",
                    reason=f"Email field is required but empty"
                )
                result.cleaned_df.at[idx, email_col] = None
                continue
            
            # Validate email format
            if "@" not in val or "." not in val.split("@")[-1]:
                result.add_error(
                    row=idx + 2, column=email_col,
                    value=val,
                    reason=f"Invalid email format: '{val}'"
                )
                result.cleaned_df.at[idx, email_col] = None

    def _get_critical_columns(self, df: DataFrame) -> list:
        critical_keywords = ["id", "order", "product", "payment"]
        return [col for col in df.columns if any(kw in col.lower() for kw in critical_keywords)]

    def _detect_id_column(self, df: DataFrame):
        return self._detect_column(df, ["order_id", "id", "transaction_id", "txn_id"])

    def _detect_column(self, df: DataFrame, keywords: list):
        for col in df.columns:
            if any(kw == col.lower() for kw in keywords):
                return col
        for col in df.columns:
            if any(kw in col.lower() for kw in keywords):
                return col
        return None

    def get_error_report(self) -> list:
        if self._result is None:
            return []
        return self._result.errors
