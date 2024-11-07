from abc import ABC,abstractmethod

class TextExtractionRepository(ABC):

    @abstractmethod
    def loadData(self):
        pass

    @abstractmethod
    def clean_text(self,data):
        pass

    @abstractmethod
    def loadMecab(self):
        pass

    @abstractmethod
    def posTag(self, mecab, text):
        pass

    @abstractmethod
    def filterWord(self,posTag):
        pass

    @abstractmethod
    def Tagging(self,tagged):
        pass