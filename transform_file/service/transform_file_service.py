from abc import ABC,abstractmethod

class TransformService(ABC):
    def __init__(self, file_path):
        self.file_path = file_path
    @abstractmethod
    def select_pdf_file(self):
        pass

    @abstractmethod
    def save_html(self, file_path, overview_text, sales_table_html):
        pass

    @abstractmethod
    def process_pdf(self):
        pass