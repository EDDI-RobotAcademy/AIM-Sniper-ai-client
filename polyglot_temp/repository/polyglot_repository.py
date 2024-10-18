from abc import ABC, abstractmethod


class PolyglotRepository(ABC):
    def generateQuestion(self, userAnswer, nextIntent):
        pass