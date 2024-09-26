from abc import ABC, abstractmethod

class InterviewPreprocessingOpenAIRepository(ABC):
    @abstractmethod
    def generateIntent(self, question):
        pass