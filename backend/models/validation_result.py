from dataclasses import dataclass, field
from pandas import DataFrame


@dataclass
class ValidationError:
    row: int
    column: str
    value: str
    reason: str

    def to_dict(self) -> dict:
        return {
            "row": self.row,
            "column": self.column,
            "value": self.value,
            "reason": self.reason
        }


@dataclass
class ValidationResult:
    worker_name: str
    is_valid: bool = True
    error_count: int = 0
    errors: list = field(default_factory=list)
    cleaned_df: DataFrame = field(default_factory=DataFrame)

    def add_error(self, row: int, column: str, value: str, reason: str):
        self.errors.append(ValidationError(row, column, value, reason).to_dict())
        self.error_count += 1
        self.is_valid = False

    def summary(self) -> dict:
        return {
            "worker": self.worker_name,
            "is_valid": self.is_valid,
            "error_count": self.error_count,
            "errors": self.errors
        }
