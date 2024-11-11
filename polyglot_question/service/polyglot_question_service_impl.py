import os
from polyglot_question.repository.polyglot_question_repository_impl import PolyglotQuestionRepositoryImpl
from polyglot_question.service.polyglot_question_service import PolyglotQuestionService


class PolyglotQuestionServiceImpl(PolyglotQuestionService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__polyglotQuestionRepository = PolyglotQuestionRepositoryImpl.getInstance()

            return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    async def generateNextQuestion(self, *arg, **kwargs):
        cacheDir = os.path.join("models", "cache")
        if not os.path.exists(cacheDir):
            self.__polyglotQuestionRepository.downloadPretrainedModel()

        userAnswer = arg[0]
        nextIntent = arg[1]

        return self.__polyglotQuestionRepository.generateQuestion(userAnswer, nextIntent)