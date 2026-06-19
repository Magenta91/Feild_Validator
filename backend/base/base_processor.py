from abc import ABC, abstractmethod
from pandas import DataFrame


class BaseProcessor(ABC):
    """
    Abstract base class that all processor workers must extend.
    Processors transform or output data (cleaning, splitting).
    """

    def __init__(self, worker_name: str):
        self.worker_name = worker_name

    @abstractmethod
    def process(self, df: DataFrame, **kwargs) -> DataFrame:
        """
        Process the dataframe and return the result.
        """
        pass

    @abstractmethod
    def get_summary(self) -> dict:
        """
        Return a summary of what was processed.
        """
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__} worker='{self.worker_name}'>"
