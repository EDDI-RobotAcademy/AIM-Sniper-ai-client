from abc import ABC,abstractmethod

class TextExtractionService(ABC):

    @abstractmethod
    def loadAndPreprocessing(self):
        pass

    @abstractmethod
    def wordTagging(self,summary):
        pass

    @abstractmethod
    def save_to_csv(self,tagged_word_counts, filename="tagged_word_counts.csv"):
        pass