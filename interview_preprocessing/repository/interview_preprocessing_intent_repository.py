from abc import ABC, abstractmethod


class InterviewPreprocessingIntentRepository(ABC):

    @abstractmethod
    def intentLabelingByRuleBase(self, interviewList):
        pass

    @abstractmethod
    def countLabeledInterview(self, labeledInterviewList):
        pass

    @abstractmethod
    def splitInterviewListByIntentIsNone(self, labeledInterviewList):
        pass

    @abstractmethod
    def sampleRandomQuestionListIntentIsNone(self, interviewListIntentIsNone, sampleSize):
        pass

    @abstractmethod
    def sampleRandomQuestionListByIntent(self, labeledInterviewList, sample_size):
        pass

    @abstractmethod
    def flattenDimensionOfList(self, doublyLinkedList):
        pass

    @abstractmethod
    def calculateDifferentIntentRatios(self, interviewList, intentKey, compareKey):
        pass
