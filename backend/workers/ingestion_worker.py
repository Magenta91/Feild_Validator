import pandas as pd
from pandas import DataFrame
from io import BytesIO
from base.base_ingestion import BaseIngestion


class IngestionWorker(BaseIngestion):
    """
    Handles reading and initial parsing of uploaded CSV files.
    Detects encoding, handles BOM characters, strips whitespace.
    """

    def __init__(self):
        super().__init__(worker_name="IngestionWorker")

    def ingest(self, file, **kwargs) -> DataFrame:
        try:
            content = file.read() if hasattr(file, 'read') else file
            # Try UTF-8 first, fall back to latin-1
            try:
                df = pd.read_csv(BytesIO(content), encoding="utf-8-sig")
            except UnicodeDecodeError:
                df = pd.read_csv(BytesIO(content), encoding="latin-1")

            # Strip whitespace from column names and string values
            df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
            df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

            self.raw_df = df
            self.row_count = len(df)
            self.column_count = len(df.columns)

            return df

        except Exception as e:
            raise ValueError(f"IngestionWorker failed to parse file: {str(e)}")

    def get_schema(self) -> dict:
        if self.raw_df is None:
            return {}
        return {
            col: str(dtype)
            for col, dtype in self.raw_df.dtypes.items()
        }
