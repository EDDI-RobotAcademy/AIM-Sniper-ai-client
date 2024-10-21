import os

from polyglot_temp.repository.polyglot_repository_impl import PolyglotRepositoryImpl
from polyglot_temp.service.polyglot_service import PolyglotService


class PolyglotServiceImpl(PolyglotService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__polyglotRepository = PolyglotRepositoryImpl.getInstance()

            return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    async def generateNextQuestion(self, *arg, **kwargs):
        cacheDir = os.path.join("models", "cache")
        if not os.path.exists(cacheDir):
            self.__polyglotRepository.downloadPretrainedModel()

        userAnswer = arg[0]
        nextIntent = arg[1]

        return self.__polyglotRepository.generateQuestion(userAnswer, nextIntent)

    async def scoreUserAnswer(self, *arg, **kwargs):
        cacheDir = os.path.join("models", "cache")
        if not os.path.exists(cacheDir):
            self.__polyglotRepository.downloadPretrainedModel()

        question = arg[0]
        userAnswer = arg[1]
        intent = arg[2]

        return self.__polyglotRepository.scoreUserAnswer(question, userAnswer, intent)

