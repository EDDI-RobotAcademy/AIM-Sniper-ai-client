from abc import ABC, abstractmethod


class InterviewPreprocessingRepository(ABC):
    @abstractmethod
    def readRawJson(self):
        pass

    @abstractmethod
    def extractColumns(self, rawDataList):
        pass

    @abstractmethod
    def separateJson(self, extractedData):
        pass