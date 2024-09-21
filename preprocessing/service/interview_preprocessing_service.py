from abc import ABC, abstractmethod


class InterviewPreprocessingService(ABC):
    @abstractmethod
    def separateDataByInfo(self):
        pass

    @abstractmethod
    def sampleInterviewData(self, nAnswer, mQuestion):
        pass

    @abstractmethod
    def transformSampledData(self, answerList, questionList):
        pass

    @abstractmethod
    def cosineSimilarityBySentenceTransformer(self, answerStringList, questionStringList):
        pass