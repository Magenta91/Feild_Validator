from abc import ABC, abstractmethod
from pandas import DataFrame


class BaseIngestion(ABC):
    """
    Abstract base class for all ingestion workers.
    Handles reading and initial parsing of uploaded files.
    """

    def __init__(self, worker_name: str):
        self.worker_name = worker_name
        self.raw_df: DataFrame = None
        self.row_count: int = 0
        self.column_count: int = 0

    @abstractmethod
    def ingest(self, file, **kwargs) -> DataFrame:
        """
        Read and parse the uploaded file.
        Must return a DataFrame.
        """
        pass

    @abstractmethod
    def get_schema(self) -> dict:
        """
        Return detected schema — column names and inferred types.
        """
        pass

    def get_stats(self) -> dict:
        return {
            "row_count": self.row_count,
            "column_count": self.column_count,
            "columns": list(self.raw_df.columns) if self.raw_df is not None else []
        }

    def __repr__(self):
        return f"<{self.__class__.__name__} worker='{self.worker_name}'>"
