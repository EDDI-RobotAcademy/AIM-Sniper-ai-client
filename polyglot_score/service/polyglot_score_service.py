from abc import ABC, abstractmethod


class PolyglotScoreService(ABC):
    @abstractmethod
    def scoreUserAnswer(self, *arg, **kwargs):
        pass