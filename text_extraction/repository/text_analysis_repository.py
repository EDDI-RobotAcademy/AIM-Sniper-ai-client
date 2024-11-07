from abc import ABC,abstractmethod

class TextAnalysisRepository(ABC):

    @abstractmethod
    def loadData(self):
        pass

    @abstractmethod
    def clean_text(self,data):
        pass
