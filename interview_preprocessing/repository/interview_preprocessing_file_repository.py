from abc import ABC, abstractmethod


class InterviewPreprocessingFileRepository(ABC):
    @abstractmethod
    def readFile(self, filePath):
        pass

    @abstractmethod
    def saveFile(self, filePath, data):
        pass

    @abstractmethod
    def extractColumns(self, filePath):
        pass

    @abstractmethod
    def separateFileByInfo(self, extractedData, filePath):
        pass

    @abstractmethod
    def samplingAnswerAndQuestionIndex(self, totalSize, n, m):
        pass

    @abstractmethod
    def extractIntent(self, interviewDataList):
        pass