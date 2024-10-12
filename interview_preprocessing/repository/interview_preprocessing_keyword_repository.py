from abc import ABC, abstractmethod


class InterviewPreprocessingKeywordRepository(ABC):
    @abstractmethod
    def decomposeHangul(self, keyword):
        pass

    @abstractmethod
    def generateQuestion(self, keyword):
        pass
