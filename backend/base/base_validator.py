from abc import ABC, abstractmethod
from pandas import DataFrame
from models.validation_result import ValidationResult


class BaseValidator(ABC):
    """
    Abstract base class that all validator workers must extend.
    Enforces a consistent interface across all validation types.
    """

    def __init__(self, worker_name: str):
        self.worker_name = worker_name
        self._result: ValidationResult = None

    @abstractmethod
    def validate(self, df: DataFrame, **kwargs) -> ValidationResult:
        """
        Run validation on the dataframe.
        Must return a ValidationResult object.
        """
        pass

    @abstractmethod
    def get_error_report(self) -> list:
        """
        Return list of all errors found during validation.
        """
        pass

    def _init_result(self, df: DataFrame) -> ValidationResult:
        """Helper to initialise a fresh ValidationResult."""
        result = ValidationResult(worker_name=self.worker_name)
        result.cleaned_df = df.copy()
        return result

    def __repr__(self):
        return f"<{self.__class__.__name__} worker='{self.worker_name}'>"
