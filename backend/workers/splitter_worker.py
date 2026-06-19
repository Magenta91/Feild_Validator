import os
import uuid
from pandas import DataFrame
from base.base_processor import BaseProcessor


class SplitterWorker(BaseProcessor):
    """
    Splits large DataFrames into smaller CSV chunks.
    Each chunk is saved temporarily and a list of paths is returned.
    """

    def __init__(self):
        super().__init__(worker_name="SplitterWorker")
        self._summary = {}
        self.chunk_paths = []

    def process(self, df: DataFrame, chunk_size: int = 1000, output_dir: str = "/tmp", **kwargs) -> DataFrame:
        self.chunk_paths = []
        total_rows = len(df)

        if total_rows <= chunk_size:
            # No splitting needed
            self._summary = {
                "total_rows": total_rows,
                "chunk_size": chunk_size,
                "chunks_created": 1,
                "splitting_applied": False
            }
            path = self._save_chunk(df, output_dir, chunk_index=0)
            self.chunk_paths.append(path)
            return df

        # Split into chunks
        chunks = [df[i:i + chunk_size] for i in range(0, total_rows, chunk_size)]
        for i, chunk in enumerate(chunks):
            path = self._save_chunk(chunk, output_dir, chunk_index=i + 1)
            self.chunk_paths.append(path)

        self._summary = {
            "total_rows": total_rows,
            "chunk_size": chunk_size,
            "chunks_created": len(chunks),
            "splitting_applied": True
        }

        return df

    def _save_chunk(self, df: DataFrame, output_dir: str, chunk_index: int) -> str:
        os.makedirs(output_dir, exist_ok=True)
        filename = f"validated_chunk_{chunk_index}_{uuid.uuid4().hex[:6]}.csv"
        path = os.path.join(output_dir, filename)
        df.to_csv(path, index=False)
        return path

    def get_summary(self) -> dict:
        return self._summary
