from abc import ABC, abstractmethod


class PolyglotRepository(ABC):
    @abstractmethod
    def downloadPretrainedModel(self):
        pass

    @abstractmethod
    def generateQuestion(self, userAnswer, nextIntent):
        pass
