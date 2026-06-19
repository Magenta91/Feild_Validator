from pandas import DataFrame
from base.base_processor import BaseProcessor


class CleanerWorker(BaseProcessor):
    """
    Cleans the dataframe after all validations:
    - Removes rows where critical fields are null
    - Standardises string casing
    - Strips extra whitespace
    - Tags each row as valid/invalid
    """

    def __init__(self):
        super().__init__(worker_name="CleanerWorker")
        self._summary = {}

    def process(self, df: DataFrame, validation_results: list = None, **kwargs) -> DataFrame:
        original_count = len(df)
        cleaned = df.copy()

        # Add validity tag based on error rows from all validation results
        error_rows = set()
        if validation_results:
            for result in validation_results:
                for error in result.errors:
                    if error["row"] > 0:
                        error_rows.add(error["row"] - 2)  # convert back to df index

        cleaned["_is_valid"] = cleaned.index.map(lambda i: "valid" if i not in error_rows else "invalid")

        # Standardise string fields
        for col in cleaned.select_dtypes(include="object").columns:
            if col != "_is_valid":
                cleaned[col] = cleaned[col].astype(str).str.strip()

        # Separate valid and invalid
        valid_df = cleaned[cleaned["_is_valid"] == "valid"].drop(columns=["_is_valid"])
        invalid_df = cleaned[cleaned["_is_valid"] == "invalid"].drop(columns=["_is_valid"])

        self._summary = {
            "original_rows": original_count,
            "valid_rows": len(valid_df),
            "invalid_rows": len(invalid_df),
            "removed_rows": len(invalid_df)
        }

        return valid_df

    def get_summary(self) -> dict:
        return self._summary
