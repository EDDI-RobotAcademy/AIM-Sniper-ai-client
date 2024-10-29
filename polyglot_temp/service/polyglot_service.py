from abc import ABC, abstractmethod


class PolyglotService(ABC):
    @abstractmethod
    def generateNextQuestion(self, *arg, **kwargs):
        pass
