from abc import ABC, abstractmethod

class InterviewPreprocessingOpenAIRepository(ABC):
    @abstractmethod
    def generateIntent(self, question):
        pass

    @abstractmethod
    def scoreAnswer(self, question, intent, answer):
        pass