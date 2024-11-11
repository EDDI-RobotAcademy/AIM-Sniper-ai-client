from abc import ABC, abstractmethod


class PolyglotQuestionRepository(ABC):
    @abstractmethod
    def downloadPretrainedModel(self):
        pass

    @abstractmethod
    def generateQuestion(self, userAnswer, nextIntent):
        pass
