from abc import ABC,abstractmethod

class TransformRepository(ABC):
    def __init__(self, file_path):
        self.file_path = file_path
    @abstractmethod
    def extract_overview_and_sales_table(self):
        pass