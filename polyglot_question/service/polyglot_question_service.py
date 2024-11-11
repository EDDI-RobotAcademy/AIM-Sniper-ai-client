from abc import ABC, abstractmethod


class PolyglotQuestionService(ABC):
    @abstractmethod
    def generateNextQuestion(self, *arg, **kwargs):
        pass
