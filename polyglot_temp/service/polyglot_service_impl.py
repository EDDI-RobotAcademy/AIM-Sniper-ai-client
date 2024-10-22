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

        interviewList = arg[0]
        print("interviewList: ", interviewList)

        resultList = []
        for interview in interviewList:
            question, userAnswer, intent = interview[0], interview[1], interview[2]
            result = self.__polyglotRepository.scoreUserAnswer(question, userAnswer, intent)
            resultList.append(result)

        return resultList

