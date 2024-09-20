from abc import ABC, abstractmethod


class InterviewPreprocessingRepository(ABC):
    @abstractmethod
    def readJsonFile(self, filePath):
        pass

    @abstractmethod
    def extractColumns(self, rawDataList):
        pass

    @abstractmethod
    def separateFileByInfo(self, extractedData):
        pass

    @abstractmethod
    def loadMecab(self):
        pass

    @abstractmethod
    def posTagging(self, mecab, text):
        pass

    @abstractmethod
    def filterWord(self, posTagging):
        pass

    @abstractmethod
    def calculateCosineSimilarity(self, filteredAnswer, filteredQuestion):
        pass