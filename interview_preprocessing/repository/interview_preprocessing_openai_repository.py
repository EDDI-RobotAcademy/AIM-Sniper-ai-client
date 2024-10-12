from abc import ABC, abstractmethod

class InterviewPreprocessingOpenAIRepository(ABC):
    @abstractmethod
    def generateIntent(self, question):
        pass

    @abstractmethod
    def scoreAnswer(self, question, intent, answer):
        pass

    @abstractmethod
    def getTechKeyword(self, role):
        pass

    @abstractmethod
    def getTechAnswer(self, question, score):
        pass

    @abstractmethod
    def createTechSession(self):
        pass