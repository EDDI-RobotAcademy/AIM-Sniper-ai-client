from abc import ABC, abstractmethod


class PolyglotScoreRepository(ABC):
    @abstractmethod
    def downloadPretrainedModel(self):
        pass

    @abstractmethod
    def scoreUserAnswer(self, question, userAnswer, intent, model, tokenizer):
        pass

    @abstractmethod
    def loadScoreModel(self):
        pass

    @abstractmethod
    def scoreUserAnswerTest(self, question, userAnswer, intent, scoreModel, tokenizer):
        pass