from abc import ABC, abstractmethod


class InterviewPreprocessingService(ABC):
    @abstractmethod
    def separateDataByInfo(self, filePath):
        pass

    @abstractmethod
    def getInterviewData(self, filePath):
        pass

    @abstractmethod
    def flattenInterviewData(self, filePath):
        pass

    @abstractmethod
    def sampleInterviewData(self, interviewList, nAnswer, mQuestion, filePath):
        pass

    @abstractmethod
    def transformSampledData(self, answerList, questionList):
        pass

    @abstractmethod
    def cosineSimilarityBySentenceTransformer(self, answerStringList, questionStringList):
        pass

    @abstractmethod
    def cosineSimilarityByNltk(self, answerStringList, questionStringList):
        pass

    @abstractmethod
    def countWantToData(self, keyword, interviewDataPath):
        pass