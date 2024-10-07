from abc import ABC, abstractmethod


class InterviewPreprocessingFileRepository(ABC):
    @abstractmethod
    def readFile(self, filePath):
        pass

    @abstractmethod
    def saveFile(self, filePath, data, silent):
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
    def splitSentenceToWord(self, interviewList):
        pass

    @abstractmethod
    def countWord(self, questionWordList, answerWordList):
        pass

    @abstractmethod
    def loadStopWordList(self):
        pass

    @abstractmethod
    def filterInterviewData(self, interviewList, stopWordList):
        pass